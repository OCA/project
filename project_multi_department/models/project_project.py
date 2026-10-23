# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    department_ids = fields.Many2many(
        comodel_name="hr.department",
        string="Project Departments",
        default=lambda self: self.env.user.employee_id.department_id,
    )
