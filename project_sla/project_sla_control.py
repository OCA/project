# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Daniel Reis
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.safe_eval import safe_eval
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DT_FMT
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT as D_FMT
from openerp import SUPERUSER_ID
from datetime import timedelta
from datetime import datetime as dt
from . import m2m

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
        if attr in obj._model._columns:
            try:
                obj = getattr(obj, attr)
            except AttributeError:
                return default
            if not obj:
                return default
        else:
            return default
    return obj


class SLAControl(orm.Model):

    """
    SLA Control Registry
    Each controlled document (Issue, Claim, ...) will have a record here.
    This model concentrates all the logic for Service Level calculation.
    """
    _name = 'project.sla.control'
    _description = 'SLA Control Registry'

    _columns = {
        'doc_id': fields.integer('Document ID', readonly=True),
        'doc_model': fields.char('Document Model', size=128, readonly=True),
        'sla_line_id': fields.many2one(
            'project.sla.line', 'Service Agreement'),
        'sla_warn_date': fields.datetime('Warning Date'),
        'sla_limit_date': fields.datetime('Limit Date'),
        'sla_start_date': fields.datetime('Start Date'),
        'sla_close_date': fields.datetime('Close Date'),
        'sla_achieved': fields.integer('Achieved?'),
        'sla_state': fields.selection(SLA_STATES, string="SLA Status"),
        'locked': fields.boolean(
            'Recalculation disabled',
            help="Safeguard manual changes from future automatic "
                 "recomputations."),
            # Future: perfect SLA manual handling
    }

    def write(self, cr, uid, ids, vals, context=None):
        """
        Update the related Document's SLA State when any of the SLA Control
        lines changes state
        """
        res = super(SLAControl, self).write(
            cr, uid, ids, vals, context=context)
        new_state = vals.get('sla_state')
        if new_state:
            # just update sla_state without recomputing the whole thing
            context = context or {}
            context['__sla_stored__'] = 1
            for sla in self.browse(cr, uid, ids, context=context):
                doc = self.pool.get(sla.doc_model).browse(
                    cr, uid, sla.doc_id, context=context)
                colors = {
                    '1': 0,
                    '3': 4,
                    '4': 3,
                    '5': 2,
                }
                if doc.sla_state < new_state:
                    doc.write(
                        {
                            'sla_state': new_state,
                            'color': colors[new_state],
                        }
                    )
        return res

    def update_sla_states(self, cr, uid, context=None):
        """
        Updates SLA States, given the current datetime:
        Only works on "open" sla states (watching, warning and will fail):
          - exceeded limit date are set to "will fail"
          - exceeded warning dates are set to "warning"
        To be used by a scheduled job.
        """
        now = dt.now().strftime(DT_FMT)
        # SLAs to mark as "will fail"
        control_ids = self.search(
            cr, uid,
            [('sla_state', 'in', ['2', '3']), ('sla_limit_date', '<', now)],
            context=context)
        self.write(cr, uid, control_ids, {'sla_state': '4'}, context=context)
        # SLAs to mark as "warning"
        control_ids = self.search(
            cr, uid,
            [('sla_state', 'in', ['2']), ('sla_warn_date', '<', now)],
            context=context)
        self.write(cr, uid, control_ids, {'sla_state': '3'}, context=context)
        return True

    def _compute_sla_date(self, cr, uid, working_hours, res_uid,
                          start_date, hours, context=None):
        """
        Return a limit datetime by adding hours to a start_date, honoring
        a working_time calendar and a resource's (res_uid) timezone and
        availability (leaves)

        Currently implemented using a binary search using
        _interval_hours_get() from resource.calendar. This is
        resource.calendar agnostic, but could be more efficient if
        implemented based on it's logic.

        Known issue: the end date can be a non-working time; it would be
        best for it to be the latest working time possible. Example:
        if working time is 08:00 - 16:00 and start_date is 19:00, the +8h
        end date will be 19:00 of the next day, and it should rather be
        16:00 of the next day.
        """
        assert isinstance(start_date, dt), (
            "start_date must be instance of 'datetime'.")
        assert isinstance(hours, int) and hours >= 0, (
            "hours must be int and >= 0. got %s" % repr(hours))

        cal_obj = self.pool.get('resource.calendar')
        target, step = hours * 3600, 16 * 3600
        lo, hi = start_date, start_date
        while target > 0 and step > 60:
            hi = lo + timedelta(seconds=step)
            check = int(3600 * cal_obj._interval_hours_get(
                cr, uid, working_hours, lo, hi,
                timezone_from_uid=res_uid, exclude_leaves=False,
                context=context))
            if check <= target:
                target -= check
                lo = hi
            else:
                step = int(step / 4.0)
        return hi

    def _get_computed_slas(self, cr, uid, doc, context=None):
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

        * Start date is used to start counting time
        * Control date, used to calculate SLA achievement, is defined in the
          SLA Definition rules.
        """
        def datetime2str(dt_value, fmt):  # tolerant datetime to string
            return dt_value and dt.strftime(dt_value, fmt) or None

        def get_sla_date(sla, doc, field='control'):
            """ Converts control field value to datetime object.
            """
            assert field in ('control', 'start'), (
                "field must be in ('control', 'start')")
            if field == 'control':
                sla_field = sla.control_field_id
            elif field == 'start':
                sla_field = sla.start_field_id

            val = getattr(doc, sla_field.name)
            if val and sla_field.ttype == 'datetime':
                return dt.strptime(val, DT_FMT)
            elif val and sla_field.ttype == 'date':
                # TODO: Is this behavior correct? I mean date of format
                # %Y-%m-%d 00:00:00
                return dt.strptime(val, D_FMT)
            return None

        res = []
        sla_ids = (safe_getattr(doc, 'analytic_account_id.sla_ids') or
                   safe_getattr(doc, 'project_id.analytic_account_id.sla_ids'))
        if not sla_ids:
            return res

        for sla in sla_ids:
            if sla.control_model != doc._table_name:
                continue  # SLA not for this model; skip

            for l in sla.sla_line_ids:
                eval_context = {'o': doc, 'obj': doc, 'object': doc}
                if not l.condition or safe_eval(l.condition, eval_context):

                    start_date = get_sla_date(sla, doc, 'start')
                    res_uid = safe_getattr(doc, 'user_id.id') or uid
                    cal = safe_getattr(
                        doc, 'project_id.resource_calendar_id.id')
                    warn_date = self._compute_sla_date(
                        cr, uid, cal, res_uid, start_date, l.warn_qty,
                        context=context)
                    lim_date = self._compute_sla_date(
                        cr, uid, cal, res_uid, warn_date,
                        l.limit_qty - l.warn_qty,
                        context=context)
                    # evaluate sla state
                    control_date = get_sla_date(sla, doc, 'control')
                    if control_date is not None:
                        if control_date > lim_date:
                            sla_val, sla_state = 0, '5'  # failed
                        else:
                            sla_val, sla_state = 1, '1'  # achieved
                    else:
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
            _logger.warning("No valid SLA rule found for %d, SLA Ids %s"
                            % (doc.id, repr([x.id for x in sla_ids])))
        return res

    def store_sla_control(self, cr, uid, docs, context=None):
        """
        Used by controlled documents to ask for SLA calculation and storage.
        ``docs`` is a Browse object
        """
        # context flag to avoid infinite loops on further writes
        context = {} if context is None else context.copy()
        if '__sla_stored__' in context:
            return False
        else:
            context['__sla_stored__'] = 1

        res = []
        for ix, doc in enumerate(docs):
            if ix and ix % 50 == 0:
                _logger.info('...%d SLAs recomputed for %s' % (ix, doc._name))
            control = {x.sla_line_id.id: x
                       for x in doc.sla_control_ids}
            sla_recs = self._get_computed_slas(cr, uid, doc, context=context)
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
            doc._model.write(  # regular users can't write on SLA Control
                cr, SUPERUSER_ID, [doc.id], vals, context=context)
        return res


class SLAControlled(orm.AbstractModel):

    """
    SLA Controlled documents: AbstractModel to apply SLA control on Models
    """
    _name = 'project.sla.controlled'
    _description = 'SLA Controlled Document'

    _columns = {
        'sla_control_ids': fields.many2many(
            'project.sla.control', string="SLA Control", ondelete='cascade'),
        'sla_state': fields.selection(
            SLA_STATES, string="SLA Status", readonly=True, select=True),
    }

    def store_sla_control(self, cr, uid, ids, context=None):
        docs = self.browse(cr, uid, ids, context=context)
        self.pool.get('project.sla.control').store_sla_control(
            cr, uid, docs, context=context)
        return True  # To be able to call from view or via RPC

    def create(self, cr, uid, vals, context=None):
        res = super(SLAControlled, self).create(cr, uid, vals, context=context)
        self.store_sla_control(cr, uid, [res], context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(SLAControlled, self).write(
            cr, uid, ids, vals, context=context)
        doc_domain = [
            ('id', 'in', ids),
            ('state', 'not in', ('cancelled', 'cancel')),
            '|', ('state', '!=', 'done'),
                 ('sla_state', 'not in', ('1', '5'))
        ]
        doc_ids = self.search(cr, uid, doc_domain, context=context)
        self.store_sla_control(cr, uid, doc_ids, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        # Unlink and delete all related Control records
        for doc in self.browse(cr, uid, ids, context=context):
            vals = [m2m.remove(x.id)[0] for x in doc.sla_control_ids]
            doc.write({'sla_control_ids': vals})
        return super(SLAControlled, self).unlink(cr, uid, ids, context=context)
