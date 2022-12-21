# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    project_type_id = fields.Many2one(
        comodel_name="project.type",
        string="Type",
        compute="_compute_project_type_id",
        store=True,
        readonly=False,
        copy=False,
        domain="[('timesheet_ok', '=', True)]",
    )

    @api.depends("task_id", "task_id.project_id")
    def _compute_project_type_id(self):
        for line in self.filtered(lambda line: not line.project_type_id):
            if (
                line.task_id
                and line.task_id.type_id
                and line.task_id.type_id.timesheet_ok
            ):
                line.project_type_id = line.task_id.type_id
            elif (
                line.project_id
                and line.project_id.type_id
                and line.project_id.type_id.timesheet_ok
            ):
                line.project_type_id = line.project_id.type_id
            else:
                line.project_type_id = False

    @api.onchange("project_type_id")
    def _onchange_project_type_id(self):
        if self.project_type_id and (not self.name or self.name == "/"):
            self.name = self.project_type_id.name
