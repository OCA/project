# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTimeTypeRule(models.Model):
    _name = "project.time.type.rule"
    _description = "Time Type defaults"
    _order = "employee_id, department_id, project_id, project_type_id"

    # name = fields.Char(string="Name", required=False)

    def name_get(self):
        def nox(r):
            return f"{r._name}:{r.id}" if r else "*"

        return [
            (
                r.id,
                f"{nox(r.employee_id)}.{nox(r.department_id)}"
                f".{nox(r.project_id)}.{nox(r.project_type_id)}",
            )
            for r in self
        ]

    time_type_id = fields.Many2one(comodel_name="project.time.type", required=True)

    # user_id = fields.Many2one(
    #    comodel_name="res.users"
    # )
    employee_id = fields.Many2one(comodel_name="hr.employee")
    department_id = fields.Many2one(comodel_name="hr.department")

    project_id = fields.Many2one(comodel_name="project.project")

    project_type_id = fields.Many2one(
        comodel_name="project.task.type",
        # domain = "[('project_ids','in', [project_id])]"
    )
