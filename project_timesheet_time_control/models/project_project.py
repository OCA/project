# Copyright 2019 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    show_time_control = fields.Selection(
        selection=[("start", "Start"), ("stop", "Stop")],
        compute="_compute_show_time_control",
        help="Indicate which time control button to show, if any.",
    )

    @api.model
    def _timesheet_running_domain(self):
        """Domain to find running timesheet lines."""
        return self.env["account.analytic.line"]._running_domain() + [
            ("project_id", "in", self.ids),
        ]

    @api.depends("allow_timesheets")
    def _compute_show_time_control(self):
        """Decide which time control button to show, if any."""
        grouped = self.env["account.analytic.line"].read_group(
            domain=self._timesheet_running_domain(),
            fields=["id"],
            groupby=["project_id"],
        )
        lines_per_project = {group["project_id"][0]: group["project_id_count"]
                             for group in grouped}
        button_per_lines = {0: "start", 1: "stop"}
        for project in self:
            if not project.allow_timesheets:
                project.show_time_control = False
                continue
            project.show_time_control = button_per_lines.get(
                lines_per_project.get(project.id, 0),
                False,
            )

    def button_start_work(self):
        """Create a new record starting now, with a running timer."""
        return {
            "context": {
                "default_project_id": self.id,
                "default_task_id": False,
            },
            "name": _("Start work"),
            "res_model": "hr.timesheet.switch",
            "target": "new",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
        }

    @api.multi
    def button_end_work(self):
        running_lines = self.env["account.analytic.line"].search(
            self._timesheet_running_domain(),
        )
        if not running_lines:
            raise UserError(
                _("No running timer found in project %s. "
                  "Refresh the page and check again.") % self.display_name,
            )
        return running_lines.button_end_work()
