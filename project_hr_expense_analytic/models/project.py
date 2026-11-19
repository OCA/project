# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    hr_expense_ids = fields.One2many("hr.expense", "project_id", string="HR Expenses")
