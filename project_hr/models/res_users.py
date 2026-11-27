# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    hr_category_ids = fields.Many2many(
        comodel_name="hr.employee.category",
        string="HR categories",
        compute="_compute_hr_category_ids",
        help="Technical field for computing dynamically employee categories "
        "linked to the user in the current company.",
    )

    @api.depends("company_id", "employee_ids", "employee_ids.category_ids")
    @api.depends_context("allowed_company_ids", "company")
    def _compute_hr_category_ids(self):
        """It is important to use the company employee (self.env.company) because
        it is possible that the user's company (user.company_id) is not listed
        as an allowed company (allowed_company_ids) and therefore the employee
        is not in the employee_ids field.
        """
        for user in self:
            user.hr_category_ids = user.employee_ids.filtered(
                lambda x, company_id=self.env.company: x.company_id == company_id
            )[:1].category_ids
