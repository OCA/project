# Copyright 2019 Tecnativa - Victor M.M. Torres
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def create(self, vals):
        employee = super().create(vals)
        if employee.category_ids:
            self.env["project.task"].invalidate_cache()
        return employee
