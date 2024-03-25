# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    default_task_template_id = fields.Many2one(comodel_name="project.task.template")
    task_template_ids = fields.Many2many(
        comodel_name="project.task.template", string="Task Templates"
    )
    template_task_type_ids = fields.Many2many(
        string="Templates allowed in stages", comodel_name="project.task.type"
    )
    is_restrict_template_by_stages = fields.Boolean(
        string="Restrict template by stages"
    )

    @api.onchange("task_template_ids")
    def _onchange_task_template_ids(self):
        for record in self:
            if record.default_task_template_id and (
                record.default_task_template_id not in record.task_template_ids
            ):
                record.default_task_template_id = False
