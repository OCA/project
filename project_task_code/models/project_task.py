# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# Copyright 2023 Abraham Anes <abrahamanes@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    code = fields.Char(
        string="Task Number",
        required=True,
        default="/",
        readonly=True,
        copy=False,
    )

    @api.constrains("code")
    def _check_project_task_unique_code(self):
        for task in self:
            if (
                task.code
                and task.code != "/"
                and self.search(
                    [
                        ("code", "=", task.code),
                        ("id", "!=", task.id),
                        ("company_id", "=", task.company_id.id),
                    ],
                    limit=1,
                )
            ):
                raise ValidationError(_("The code must be unique!"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "/") == "/":
                company_id = vals.get("company_id")
                company = (
                    self.env["res.company"].browse(company_id)
                    if company_id
                    else self._default_company_id()
                )
                if company.project_task_seq_id:
                    vals["code"] = company.project_task_seq_id._next()
        return super().create(vals_list)

    def name_get(self):
        result = super().name_get()
        new_result = []

        for task in result:
            rec = self.browse(task[0])
            name = (
                "[{}] {}".format(rec.code, task[1])
                if rec.code and rec.code != "/"
                else task[1]
            )
            new_result.append((rec.id, name))
        return new_result
