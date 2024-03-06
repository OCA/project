# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.osv import expression


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
        ("project_task_unique_code", "UNIQUE (code)", _("The code must be unique!")),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        new_list = []
        for vals in vals_list:
            if vals.get("code", "/") == "/":
                new_vals = dict(
                    vals,
                    code=self.env["ir.sequence"].next_by_code("project.task") or "/",
                )
            else:
                new_vals = vals
            new_list.append(new_vals)
        return super().create(new_list)

    def name_get(self):
        result = super().name_get()
        new_result = []

        for task in result:
            rec = self.browse(task[0])
            name = "[{}] {}".format(rec.code, task[1])
            new_result.append((rec.id, name))
        return new_result

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100):
        """Allow searching by code by default."""
        if name and operator in ["=", "ilike", "=ilike", "like", "=like"]:
            args = (
                expression.OR([[("code", operator, name)], args])
                if args
                # The parent method adds the Name to the search domain. As a
                # consequence of this action, when the args parameter is empty in the
                # inherited method, an incomplete OR term must be added. Without this
                # addition, the search domain would default to using an AND operator.
                else ["|", ("code", operator, name)]
            )
        return super()._name_search(
            name=name, args=args, operator=operator, limit=limit
        )
