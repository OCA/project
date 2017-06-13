# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class TaskMaterial(models.Model):
    _inherit = "project.task.material"

    other_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Other Partner",
        domain="['|', ('parent_id', '=', False), ('is_company', '=', True)]",
    )

    @api.multi
    def _prepare_analytic_line(self):
        res = super(TaskMaterial, self)._prepare_analytic_line()
        self.ensure_one()
        analytic_account = (
            getattr(self.task_id, 'analytic_account_id', False) or
            self.task_id.project_id.analytic_account_id)
        res['other_partner_id'] = (
            self.other_partner_id.id or
            self.task_id.partner_id != analytic_account.partner_id and
            self.task_id.partner_id.id)
        return res
