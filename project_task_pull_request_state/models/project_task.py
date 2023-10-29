# Copyright Cetmix OU 2023
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    pr_state = fields.Selection(
        selection=lambda self: self.selection_pr_state(),
        tracking=True,
        copy=False,
        string="PR State",
        compute="_compute_pr_state",
        precompute=True,
        store=True,
        readonly=False,
    )

    def selection_pr_state(self):
        """Function to select the state of the pull request"""
        return [
            ("open", "Open"),
            ("draft", "Draft"),
            ("merged", "Merged"),
            ("closed", "Closed"),
        ]

    @api.depends("pr_uri")
    def _compute_pr_state(self):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        pr_state_default = ICPSudo.get_param(
            "project_task_pull_request_state.pr_state_default"
        )
        for task in self:
            if not task.pr_uri:
                task.pr_state = False
            elif task.project_id and task.project_id.pr_state_default:
                task.pr_state = task.project_id.pr_state_default
            else:
                task.pr_state = pr_state_default or False
