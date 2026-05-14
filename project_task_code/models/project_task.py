# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"
    _rec_names_search = ["name", "code"]

    code = fields.Char(
        string="Task Number",
        required=True,
        default="/",
        readonly=True,
        copy=False,
    )

    _code_company_uniq = models.Constraint(
        "unique (company_id, code)",
        "The code must be unique!",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "/") == "/":
                vals["code"] = (
                    self.sudo().env["ir.sequence"].next_by_code("project.task") or "/"
                )
        return super().create(vals_list)

    @api.depends("name", "code")
    def _compute_display_name(self):
        result = super()._compute_display_name()
        for task in self:
            if task.code and task.code != "/" and task.display_name:
                task.display_name = f"[{task.code}] {task.display_name}"
        return result
