# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    project_id = fields.Many2one("project.project")
    task_id = fields.Many2one(
        "project.task",
        domain="[('project_id', '=', project_id)]",
    )

    @api.depends("project_id")
    def _compute_analytic_distribution(self):
        """Compute the analytic distribution based on the project linked to the expense
        report. Will remove the line if we remove the project.
        """
        res = super()._compute_analytic_distribution()
        for expense in self:
            expense.analytic_distribution = (
                expense.project_id._get_analytic_distribution()
            )
        return res

    @api.constrains("project_id", "task_id")
    def _check_task_belongs_to_project(self):
        for expense in self:
            if expense.task_id and expense.task_id.project_id != expense.project_id:
                raise ValidationError(
                    self.env._(
                        "The selected task does not belong to the selected project."
                    )
                )
