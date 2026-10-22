# Copyright 2026 Forgeflow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "/") != "/":
                continue
            project_id = vals.get("project_id")
            if not project_id:
                continue
            project = self.env["project.project"].browse(project_id)
            if project.task_sequence_id:
                vals["code"] = project.task_sequence_id.next_by_id() or "/"
        return super().create(vals_list)
