# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    code = fields.Char(
        string="Task Number",
        required=True,
        default="/",
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        (
            "project_task_unique_code",
            "UNIQUE (company_id, code)",
            _("The code must be unique!"),
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "/") == "/":
                vals["code"] = (
                    self.env["ir.sequence"].next_by_code("project.task") or "/"
                )
        return super().create(vals_list)

    @api.depends("name", "code")
    def _compute_display_name(self):
        for task in self:
            task.display_name = f"[{task.code}] {task.name}" if task.code else task.name
