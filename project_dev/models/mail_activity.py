# Copyright 2020 Advitus MB
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    dev_message = fields.Text(
        string="Dev Alert Message",
        compute="_compute_dev_message",
        default="",
    )

    @api.depends("user_id")
    def _compute_dev_message(self):
        for rec in self:
            message = ""
            if self.env.context.get("default_res_model") == "project.task":
                task = self.env["project.task"].browse(
                    self.env.context.get("default_res_id")
                )
                project_dev_group = rec.user_id.has_group(
                    "project_dev.project_devs_group"
                )
                if project_dev_group and rec.user_id:
                    if rec.user_id.id not in task.dev_ids.ids:
                        message = _(
                            "This user is not set as dev for this task and "
                            "they will not be able to see this task"
                        )
            rec.dev_message = message
