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
    # Tasks of a project displaying the number alone need no title, so the
    # requirement is moved to the view, where it only applies to projects
    # displaying the title.
    name = fields.Char(required=False)
    task_name_display = fields.Selection(
        related="project_id.task_name_display",
        readonly=True,
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

    def copy_data(self, default=None):
        vals_list = super().copy_data(default=default)
        for task, vals in zip(self, vals_list, strict=True):
            # An untitled task must stay untitled, instead of getting the
            # "False (copy)" title built by the standard copy.
            if not task.name and not (default or {}).get("name"):
                vals["name"] = False
        return vals_list

    @api.depends("name", "code", "task_name_display")
    def _compute_display_name(self):
        result = super()._compute_display_name()
        for task in self:
            if not task.code or task.code == "/":
                continue
            name = task.display_name
            if task.task_name_display == "code" or not name:
                task.display_name = task.code
            else:
                task.display_name = f"[{task.code}] {name}"
        return result
