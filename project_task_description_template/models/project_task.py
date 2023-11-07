# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    task_template_id = fields.Many2one(
        string="Template", comodel_name="project.task.template"
    )

    template_visible = fields.Boolean(compute="_compute_template_visible")

    @api.depends("project_id")
    def _compute_template_visible(self):
        for rec in self:
            if (
                rec.stage_id
                and rec.project_id
                and rec.project_id.template_task_type_ids.ids
                and rec.stage_id.id in rec.project_id.template_task_type_ids.ids
            ):
                self.template_visible = True
            else:
                self.template_visible = False

    @api.onchange("task_template_id")
    def _onchange_task_template_id(self):
        if self.task_template_id:
            self.update(
                {
                    "user_id": self.task_template_id.user_id.id,
                    "tag_ids": self.task_template_id.tag_ids,
                    "description": self.task_template_id.description,
                }
            )
