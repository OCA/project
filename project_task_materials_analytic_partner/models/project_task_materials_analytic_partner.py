# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models


class TaskMaterials(models.Model):
    _inherit = "project.task.materials"

    to_invoice = fields.Many2one(
        comodel_name='hr_timesheet_invoice.factor',
        string='Invoiceable')
    other_partner_id = fields.Many2one(
        comodel_name='res.partner', string="Other Partner",
        domain="['|', ('parent_id', '=', False), ('is_company', '=', True)]")

    @api.multi
    def _prepare_analytic_line(self):
        res = super(TaskMaterials, self)._prepare_analytic_line()
        self.ensure_one()
        res['to_invoice'] = self.to_invoice.id
        analytic_account = (
            getattr(self.task_id, 'analytic_account_id', False) or
            self.task_id.project_id.analytic_account_id)
        res['other_partner_id'] = (
            self.other_partner_id.id or
            self.task_id.partner_id != analytic_account.partner_id and
            self.task_id.partner_id.id)
        return res
