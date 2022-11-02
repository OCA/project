# Copyright 2023 Abraham Anes <abrahamanes@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    project_task_seq_id = fields.Many2one(
        string="Project task sequence",
        related="company_id.project_task_seq_id",
        readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    def set_values(self):
        res = super().set_values()
        # Assign code to tasks without code
        if self.project_task_seq_id:
            no_code_tasks = self.env["project.task"].search(
                [("code", "=", "/"), ("company_id", "=", self.company_id.id)]
            )
            for task in no_code_tasks:
                task.code = self.project_task_seq_id.next_by_id()
        return res
