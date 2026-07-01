# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, models
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _ticket_conversion_blocked(self):
        """Conversion is blocked when the company restricts it and the task's
        project is not visible to invited portal users."""
        self.ensure_one()
        company = self.company_id or self.env.company
        if not company.restrict_ticket_conversion:
            return False
        return self.project_id.privacy_visibility != "portal"

    def action_convert_to_ticket(self):
        blocked = self.filtered(lambda task: task._ticket_conversion_blocked())
        if blocked:
            raise UserError(
                _(
                    "Task-to-ticket conversion is limited to projects shared "
                    "with invited portal users. The following tasks can not be "
                    "converted: %(tasks)s.",
                    tasks=", ".join(blocked.mapped("display_name")),
                )
            )
        return super().action_convert_to_ticket()
