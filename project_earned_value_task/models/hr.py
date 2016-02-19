# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, api, exceptions, _


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    @api.model
    def get_employee_cost(self, user_id):
        employee_ids = self.search([('user_id', '=', user_id)])
        if not employee_ids:
            raise exceptions.Warning(
                _('Error!:: No employee is assigned to user.'))
        for employee in employee_ids:
            if not employee.product_id:
                raise exceptions.Warning(
                    _('Error!:: No product is assigned to employee %s.'),
                    (employee.name,))
            return employee.product_id.standard_price
