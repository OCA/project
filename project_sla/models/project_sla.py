# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ProjectSla(models.Model):
    """
    SLA Definition
    """
    _name = 'project.sla'
    _description = 'SLA Definition'

    name = fields.Char('Title', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    control_model = fields.Char('For documents', required=True)
    control_field_id = fields.Many2one(
        'ir.model.fields', string='Control Date', required=True,
        domain="[('model_id.model', '=', control_model),"
               " ('ttype', 'in', ['date', 'datetime'])]",
        help="Date field used to check if the SLA was achieved.")
    sla_line_ids = fields.One2many(
        'project.sla.line', 'sla_id', string='Definitions')
    analytic_ids = fields.Many2many(
        'account.analytic.account', string='Contracts')

    @api.multi
    def reapply_slas(self):
        """
        Force SLA recalculation on all _open_ Contracts for the selected SLAs.
        To use upon SLA Definition modifications.
        """
        for sla in self:
            sla.analytic_ids.filtered(
                lambda r: r.state == 'open')._reapply_sla()
        return True


class ProjectSlaLine(models.Model):
    """
    SLA Definition Rule Lines
    """
    _name = 'project.sla.line'
    _definition = 'SLA Definition Rule Lines'
    _order = 'sla_id,sequence'

    sla_id = fields.Many2one('project.sla', string='SLA Definition')
    sequence = fields.Integer('Sequence')
    name = fields.Char('Title', required=True, translate=True)
    condition = fields.Char(
        string='Condition', help="Apply only if this expression is "
        "evaluated to True. The document fields can be accessed using "
        "either o, obj or object. Example: obj.priority <= '2'")
    limit_qty = fields.Integer('Hours to Limit')
    warn_qty = fields.Integer('Hours to Warn')
