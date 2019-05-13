# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    @api.model
    def _update_project_soline_mapping(self, vals):
        employee = None
        if 'employee_id' in vals:
            employee = self.env['hr.employee'].browse(vals['employee_id'])
        elif self.env.user.employee_ids:
            employee = self.env.user.employee_ids[0]

        if employee and 'project_id' in vals:
            project = self.env['project.project'].browse(vals['project_id'])
            so = project.sale_order_id
            if all(not sol.product_id.seniority_level_id
                   for sol in so.order_line):
                # the sale order does not exist, or it does not use seniority
                # products at all -> don't enforce seniority on employee
                # use case : projects not related to a SO or totally fixed
                # price projects
                return
            if not employee.seniority_level_id:
                raise UserError(
                    _('''Employee with no seniority level can not timesheet
                         on project, contact your HR department.
                      '''
                      )
                )
            # Check for existing mapping in project configuration
            employee_mapped_line = project.sale_line_employee_ids.filtered(
                lambda r: r.employee_id.id == employee.id
            )
            if employee_mapped_line:
                # already mapped -> nothing to do
                return
            # Find a line on the sale order with the same seniority level
            for so_line in so.order_line:
                line_seniority = so_line.product_id.seniority_level_id
                if line_seniority == employee.seniority_level_id:
                    break
            else:
                # no line found, create the missing mapped line
                so_line = so.add_product_with_specific_seniority_level(
                    employee)
            project.sudo().write(
                {
                    'sale_line_employee_ids': [
                        (
                            0,
                            False,
                            {
                                'employee_id': employee.id,
                                'sale_line_id': so_line.id,
                            },
                        )
                    ]
                }
            )

    @api.model
    def create(self, vals):
        self._update_project_soline_mapping(vals)
        return super().create(vals)
