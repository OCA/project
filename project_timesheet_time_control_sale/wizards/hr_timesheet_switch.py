# Copyright 2019 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, models
from odoo.exceptions import UserError

# code below needs adjustments to achieve good function overriding


class HrTimesheetSwitch(models.TransientModel):
    _inherit = "hr.timesheet.switch"

    @api.model
    def _default_running_timer_id(self, employee=None):
        """Obtain running timer."""
        employee = employee or self.env.user.employee_ids
        # Find running work
        running = self.env["account.analytic.line"].search(
            [
                ("date_time", "!=", False),
                ("employee_id", "in", employee.ids),
                ("id", "not in", self.env.context.get("resuming_lines", [])),
                ("project_id", "!=", False),
                ("unit_amount", "=", 0),
                ("timesheet_invoice_id", "=", False),  # include only uninvoiced lines
            ]
        )
        if len(running) > 1:
            raise UserError(
                _(
                    "%d running timers found. Cannot know which one to stop. "
                    "Please stop them manually."
                )
                % len(running)
            )
        return running
