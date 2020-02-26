# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    hr_category_ids = fields.Many2many(
        comodel_name="hr.employee.category",
        string="Employee Categories",
        help="Here you can link the project to several employee categories, "
        "that will be the allowed in tasks.",
    )
