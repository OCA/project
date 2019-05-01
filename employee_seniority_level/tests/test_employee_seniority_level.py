# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestEmployeeSecurityLevel(SavepointCase):
    """  """

    def setUp(self):
        super().setUp()
        self.env = self.env(
            context=dict(self.env.context, tracking_disable=True)
        )
        self.levelpro = self.env['hr.employee.seniority.level'].create(
            {'sequence': 1, 'code': 'PRO', 'name': 'Professional'}
        )
        self.employee = self.env['hr.employee'].create(
            {'name': 'John Doe', 'seniority_level_id': self.levelpro.id}
        )
        self.customer = self.env['res.partner'].create({'name': 'Customer'})
        self.product1 = self.env.ref('product.product_product_1')
        self.product2 = self.env.ref('product.product_product_2')
        self.so = self.env['sale.order'].create(
            {'name': 'sale linked to project', 'partner_id': self.customer.id}
        )
        self.so.order_line = [
            (0, False, {'product_id': self.product1.id, 'product_uom_qty': 3})
        ]
        self.project = self.env['project.project'].create(
            {'name': 'Test Project', 'sale_order_id': self.so.id}
        )
        self.aal_model = self.env['account.analytic.line']

    def test_employee_no_seniority_level_can_not_timesheet_on_project(self):
        """Check employee with no seniority level.

        Employee with no seniority level set can not timesheet on projects.
        """
        self.employee.seniority_level_id = None
        with self.assertRaises(UserError):
            self.aal_model.create(
                {
                    'project_id': self.project.id,
                    'employee_id': self.employee.id,
                    'name': 'ts',
                }
            )

    def test_no_product_with_same_seniority_level_than_employee_anywhere(self):
        """Check no product with same seniority level.

        If there is not product with the same seniority level in the whole
        application. An error is raised and no timesheet is allowed on the
        project.
        """
        with self.assertRaises(UserError):
            self.aal_model.create(
                {
                    'project_id': self.project.id,
                    'employee_id': self.employee.id,
                    'name': 'ts',
                }
            )

    def test_no_product_same_seniority_level_than_employee_in_mappings(self):
        """Check creation of employee/sale order line mapping.

        When none exist a mapping with the corresponding sale order line
        is created in the project configuration.
        """
        self.assertEqual(0, len(self.project.sale_line_employee_ids))
        sol_qty = len(self.so.order_line)
        self.product2.seniority_level_id = self.levelpro
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'employee_id': self.employee.id,
                'name': 'ts',
            }
        )
        self.assertEqual(sol_qty + 1, len(self.so.order_line))
        self.assertEqual(1, len(self.project.sale_line_employee_ids))
        # And a second time, check with an existing sale order line
        self.project.sale_line_employee_ids.unlink()
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'employee_id': self.employee.id,
                'name': 'ts 2',
            }
        )
        self.assertEqual(sol_qty + 1, len(self.so.order_line))
        self.assertEqual(1, len(self.project.sale_line_employee_ids))

    def test_mapping_on_project_configuration_exists(self):
        """Check when mapping already exists.

        When a mapping employee/sale order line already exists in the project
        configuration. The timesheet should be created without any other
        actions.
        """
        self.project.write(
            {
                'sale_line_employee_ids': [
                    (
                        0,
                        False,
                        {
                            'employee_id': self.employee.id,
                            'sale_line_id': self.so.order_line[0].id,
                        },
                    )
                ]
            }
        )
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'employee_id': self.employee.id,
                'name': 'ts',
            }
        )
        self.assertEqual(1, len(self.project.sale_line_employee_ids))
        self.assertEqual(1, len(self.so.order_line))
        # Test using the employee connected to the user
        self.env.user.write({
            'employee_ids' : [(4, self.employee.id, False)]
        })
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'name': 'ts',
            }
        )
