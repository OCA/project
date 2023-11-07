# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    task_template_id = fields.Many2one(
        comodel_name="project.task.template",
        compute="_compute_template_visible",
        store=True,
        readonly=False,
    )
    template_visible = fields.Boolean(compute="_compute_template_visible", store=True)

    @api.depends("project_id", "stage_id")
    def _compute_template_visible(self):
        for rec in self:
            visible = not rec.project_id.is_restrict_template_by_stages or (
                rec.stage_id
                and rec.project_id
                and rec.project_id.template_task_type_ids
                and rec.stage_id in rec.project_id.template_task_type_ids
            )
            rec.template_visible = visible
            if (
                visible
                and rec.project_id.default_task_template_id
                and not rec.task_template_id
            ):
                rec.task_template_id = rec.project_id.default_task_template_id
                self._onchange_task_template_id()

    @api.onchange("task_template_id")
    def _onchange_task_template_id(self):
        if self.task_template_id:
            self.update(
                {
                    "user_id": self.task_template_id.user_id.id,
                    "tag_ids": self.task_template_id.tag_ids.ids,
                    "description": self.task_template_id.description,
                }
            )
