# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from openerp.tools.safe_eval import safe_eval
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DT_FMT
from odoo import SUPERUSER_ID
from datetime import datetime as dt
from odoo.addons.project_sla import m2m

import logging
_logger = logging.getLogger(__name__)


SLA_STATES = [('5', 'Failed'), ('4', 'Will Fail'), ('3', 'Warning'),
              ('2', 'Watching'), ('1', 'Achieved')]


def safe_getattr(obj, dotattr, default=False):
    """
    Follow an object attribute dot-notation chain to find the leaf value.
    If any attribute doesn't exist or has no value, just return False.
    Checks hasattr ahead, to avoid ORM Browse log warnings.
    """
    attrs = dotattr.split('.')
    while attrs:
        attr = attrs.pop(0)
        if attr in obj._fields:
            try:
                obj = getattr(obj, attr)
            except AttributeError:
                return default
            if not obj:
                return default
        else:
            return default
    return obj


class ProjectSlaControl(models.Model):
    """
    SLA Control Registry
    Each controlled document (Issue, Claim, ...) will have a record here.
    This model concentrates all the logic for Service Level calculation.
    """
    _name = 'project.sla.control'
    _description = 'SLA Control Registry'

    doc_id = fields.Integer('Document ID', readonly=True)
    doc_model = fields.Char('Document Model', size=128, readonly=True)
    sla_line_id = fields.Many2one(
        'project.sla.line', 'Service Agreement')
    sla_warn_date = fields.Datetime('Warning Date')
    sla_limit_date = fields.Datetime('Limit Date')
    sla_start_date = fields.Datetime('Start Date')
    sla_close_date = fields.Datetime('Close Date')
    sla_achieved = fields.Integer('Achieved?')
    sla_state = fields.Selection(SLA_STATES, string="SLA Status")
    locked = fields.Boolean(
        'Recalculation disabled',
        help="Safeguard manual changes from future automatic "
             "recomputations.")

    @api.multi
    def write(self, vals):
        """
        Update the related Document's SLA State when any of the SLA Control
        lines changes state
        """
        res = super(ProjectSlaControl, self).write(vals)
        new_state = vals.get('sla_state')
        if new_state:
            for sla in self.with_context({'__sla_stored__': 1}):
                doc = self.env[sla.doc_model].browse(sla.doc_id)
                if doc.sla_state < new_state:
                    doc.write({'sla_state': new_state})
        return res

    @api.model
    def update_sla_states(self):
        """
        Updates SLA States, given the current datetime:
        Only works on "open" sla states (watching, warning and will fail):
          - exceeded limit date are set to "will fail"
          - exceeded warning dates are set to "warning"
        To be used by a scheduled job.
        """
        now = dt.strftime(dt.now(), DT_FMT)
        # SLAs to mark as "will fail"
        controls = self.search(
            [('sla_state', 'in', ['2', '3']), ('sla_limit_date', '<', now)], )
        if controls:
            controls.write({'sla_state': '4'})
        # SLAs to mark as "warning"
        controls = self.search(
            [('sla_state', 'in', ['2']), ('sla_warn_date', '<', now)], )
        if controls:
            controls.write({'sla_state': '3'})
        return True

    @api.multi
    def _compute_sla_date(self, calendar_id, resource_id, start_date, hours):
        """
        Return a limit datetime by adding hours to a start_date, honoring
        a working_time calendar and a resource's (res_uid) timezone and
        availability (leaves)
        """
        assert isinstance(start_date, dt)
        assert isinstance(hours, int) and hours >= 0
        periods = self.env['resource.calendar'].browse(
            calendar_id)._schedule_hours(
                hours,
                day_dt=start_date,
                compute_leaves=True,
                resource_id=resource_id,
                default_interval=(8, 16))
        end_date = periods[-1][1]
        return end_date

    @api.model
    def _get_computed_slas(self, doc):
        """
        Returns a dict with the computed data for SLAs, given a browse record
        for the target document.

        * The SLA used is either from a related analytic_account_id or
          project_id, whatever is found first.
        * The work calendar is taken from the Project's definitions ("Other
          Info" tab -> Working Time).
        * The timezone used for the working time calculations are from the
          document's responsible User (user_id) or from the current User (uid).

        For the SLA Achieved calculation:

        * Creation date is used to start counting time
        * Control date, used to calculate SLA achievement, is defined in the
          SLA Definition rules.
        """
        def datetime2str(dt_value, fmt):  # tolerant datetime to string
            return dt_value and dt.strftime(dt_value, fmt) or None

        res = []
        sla_ids = (safe_getattr(doc, 'analytic_account_id.sla_ids') or
                   safe_getattr(doc, 'project_id.analytic_account_id.sla_ids'))
        if not sla_ids:
            return res

        for sla in sla_ids:
            if sla.control_model != doc._name:
                continue  # SLA not for this model; skip

            for l in sla.sla_line_ids:
                eval_context = {'o': doc, 'obj': doc, 'object': doc}
                if not l.condition or safe_eval(l.condition, eval_context):
                    start_date = dt.strptime(doc.create_date, DT_FMT)
                    res_uid = doc.user_id.id or self.env.user.id
                    cal = safe_getattr(
                        doc, 'project_id.resource_calendar_id.id')
                    warn_date = self._compute_sla_date(
                        cal, res_uid, start_date, l.warn_qty)
                    lim_date = self._compute_sla_date(
                        cal, res_uid, warn_date, l.limit_qty - l.warn_qty)
                    # evaluate sla state
                    control_val = getattr(doc, sla.control_field_id.name)
                    if control_val:
                        control_date = dt.strptime(control_val, DT_FMT)
                        if control_date > lim_date:
                            sla_val, sla_state = 0, '5'  # failed
                        else:
                            sla_val, sla_state = 1, '1'  # achieved
                    else:
                        control_date = None
                        now = dt.now()
                        if now > lim_date:
                            sla_val, sla_state = 0, '4'  # will fail
                        elif now > warn_date:
                            sla_val, sla_state = 0, '3'  # warning
                        else:
                            sla_val, sla_state = 0, '2'  # watching

                    res.append(
                        {'sla_line_id': l.id,
                         'sla_achieved': sla_val,
                         'sla_state': sla_state,
                         'sla_warn_date': datetime2str(warn_date, DT_FMT),
                         'sla_limit_date': datetime2str(lim_date, DT_FMT),
                         'sla_start_date': datetime2str(start_date, DT_FMT),
                         'sla_close_date': datetime2str(control_date, DT_FMT),
                         'doc_id': doc.id,
                         'doc_model': sla.control_model})
                    break

        if sla_ids and not res:
            _logger.warning("No valid SLA rule foun for %d, SLA Ids %s"
                            % (doc.id, repr([x.id for x in sla_ids])))
        return res

    @api.model
    def store_sla_control(self, docs):
        """
        Used by controlled documents to ask for SLA calculation and storage.
        ``docs`` is a Recordset
        """
        # context flag to avoid infinite loops on further writes
        if '__sla_stored__' in self.env.context:
            return False
        else:
            docs = docs.with_context({'__sla_stored__': 1})
            self = self.with_context({'__sla_stored__': 1})

        res = []
        for ix, doc in enumerate(docs):
            if ix and ix % 50 == 0:
                _logger.info('...%d SLAs recomputed for %s' % (ix, doc._name))
            control = {x.sla_line_id.id: x for x in doc.sla_control_ids}
            sla_recs = self._get_computed_slas(doc)
            # calc sla control lines
            if sla_recs:
                slas = []
                for sla_rec in sla_recs:
                    sla_line_id = sla_rec.get('sla_line_id')
                    if sla_line_id in control:
                        control_rec = control.get(sla_line_id)
                        if not control_rec.locked:
                            slas += m2m.write(control_rec.id, sla_rec)
                    else:
                        slas += m2m.add(sla_rec)
                global_sla = max([sla[2].get('sla_state') for sla in slas])
            else:
                slas = m2m.clear()
                global_sla = None
            # calc sla control summary and store
            vals = {'sla_state': global_sla, 'sla_control_ids': slas}
            # regular users can't write on SLA Control
            doc.sudo().write(vals)
        return res


class ProjectSlaControlled(models.AbstractModel):
    """
    SLA Controlled documents: AbstractModel to apply SLA control on Models
    """
    _name = 'project.sla.controlled'
    _description = 'SLA Controlled Document'
    
    sla_control_ids = fields.Many2many(
        'project.sla.control', string="SLA Control", ondelete='cascade')
    sla_state = fields.Selection(
        SLA_STATES, string="SLA Status", readonly=True)

    @api.model
    def create(self, vals):
        res = super(ProjectSlaControlled, self).create(vals)
        self.env['project.sla.control'].store_sla_control(res)
        return res

    @api.multi
    def write(self, vals):
        res = super(ProjectSlaControlled, self).write(vals)
        # docs = [x for x in self
        #         if (not x.stage_id.fold or x.sla_state not in ['1', '5'])]
        docs = self.filtered(
            lambda r:
            r.stage_id.fold is not False or r.sla_state not in ['1', '5'])
        self.env['project.sla.control'].store_sla_control(docs)
        return res

    @api.multi
    def unlink(self):
        # Unlink and delete all related Control records
        for doc in self:
            vals = [m2m.remove(x.id)[0] for x in doc.sla_control_ids]
            doc.write({'sla_control_ids': vals})
        return super(ProjectSlaControlled, self).unlink()
