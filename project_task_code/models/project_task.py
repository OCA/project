# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


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
                # Check if data inserted ir.sequence exists
                sequence_id = self.env.ref(
                    "project_task_code.sequence_task", raise_if_not_found=False
                )
                if not sequence_id:
                    # If not exists, check if there is other register with the same code
                    next_code = (
                        self.env["ir.sequence"].next_by_code("project.task") or False
                    )
                    if not next_code:
                        raise UserError(
                            _(
                                "There must be at least one sequence with code 'project.task'"
                            )
                        )
                else:
                    next_code = sequence_id.next_by_id()

                new_vals = dict(
                    vals,
                    code=next_code or "/",
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
