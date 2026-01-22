# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    budget_threshold = fields.Float()
    total_budget_amount_threshold = fields.Monetary(
        compute="_compute_budget_amount_threshold"
    )
    is_budget_exceeded = fields.Boolean(default=False)
    force_notification_send = fields.Boolean(default=False)
    create_activity_for_project_manager = fields.Boolean(default=False)

    @api.depends("total_budget_amount", "budget_threshold")
    def _compute_budget_amount_threshold(self):
        for rec in self:
            rec.total_budget_amount_threshold = (
                rec.total_budget_amount * rec.budget_threshold
            )

    def _cron_find_budget_threshold_exceeded(self):
        exceeded_projects = self.env["project.project"].search(
            [("budget_threshold", "<=", "total_budget_progress")]
        )
        for project in exceeded_projects:
            project.write({"is_budget_exceeded": True})
            if project.user_id.partner_id.id not in project.message_partner_ids.ids:
                project.message_partner_ids += project.user_id.partner_id
            template = (
                "project_budget_threshold_alert.project_budget_exceeded_email_template"
            )
            project.message_post_with_source(source_ref=template)
