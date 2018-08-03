# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Task(models.Model):
    _inherit = 'project.task'

    @api.multi
    def _project_complete_wbs_name(self):
        if not self._ids:
            return []
        res = []
        data_project = []
        for task in self:
            if task.project_id:
                data_project = task.project_id.complete_wbs_name
            if data_project:
                res.append((task.id, data_project))
            else:
                res.append((task.id, ''))
        return dict(res)

    @api.multi
    def _project_complete_wbs_code(self):
        if not self._ids:
            return []
        res = []
        data_project = []
        for task in self:
            if task.project_id:
                data_project = task.project_id.complete_wbs_code
            if data_project:
                res.append((task.id, data_project))
            else:
                res.append((task.id, ''))
        return dict(res)

    analytic_account_id = fields.Many2one(
        related='project_id.analytic_account_id',
        relation='account.analytic.account',
        string='Analytic Account', store=True, readonly=True
    )
    project_complete_wbs_code = fields.Char(
        'Full WBS Code',
        related='analytic_account_id.complete_wbs_code',
        readonly=True
    )
    project_complete_wbs_name = fields.Char(
        'Full WBS Name',
        related='analytic_account_id.complete_wbs_name',
        readonly=True
    )
