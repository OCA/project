# Copyright 2020 Advitus MB
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    task_team_member_message = fields.Text(
        string="Task Team Alert Message",
        compute="_compute_task_team_member_message",
        default="",
    )

    @api.depends("user_id")
    def _compute_task_team_member_message(self):
        for rec in self:
            message = ""
            if self.env.context.get("default_res_model") == "project.task":
                task = self.env["project.task"].browse(
                    self.env.context.get("default_res_id")
                )
                project_task_team_member_group = rec.user_id.has_group(
                    "project_task_team.project_task_group"
                )
                if project_task_team_member_group and rec.user_id:
                    if rec.user_id.id not in task.task_team_ids.ids:
                        message = _(
                            "This user is not set as a team member for this task and "
                            "they will not be able to see this task"
                        )
            rec.task_team_member_message = message
