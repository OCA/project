# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    hr_category_ids = fields.Many2many(
        comodel_name="hr.employee.category",
        string="HR categories",
        compute="_compute_hr_category_ids",
        help="Technical field for computing dynamically employee categories "
             "linked to the user in the current company."
    )

    @api.depends('company_id', 'employee_ids', 'employee_ids.category_ids')
    def _compute_hr_category_ids(self):
        for user in self:
            user.hr_category_ids = user.employee_ids.filtered(
                lambda x: x.company_id == user.company_id
            )[:1].category_ids
