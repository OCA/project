# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo.tests.common import TransactionCase


class TestProjectSaleOrderLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Creare project
        Project = cls.env["project.project"].with_context(tracking_disable=True)
        cls.project_test = Project.create(
            {
                "name": "Test Project Sale Order Link",
                "allow_timesheets": True,
                "allow_billable": True,
            }
        )

        # Create service products
        uom_hour = cls.env.ref("uom.product_uom_hour")
        Product = cls.env["product.product"].with_context(tracking_disable=True)
        cls.product1 = Product.create(
            {
                "name": "Service Ordered, create task in test project",
                "standard_price": 30,
                "list_price": 90,
                "type": "service",
                "invoice_policy": "order",
                "uom_id": uom_hour.id,
                "uom_po_id": uom_hour.id,
                "default_code": "SERV-ORDERED",
                "service_type": "timesheet",
                "service_tracking": "task_global_project",
                "project_id": cls.project_test.id,
                "taxes_id": False,
            }
        )
        cls.product2 = Product.create(
            {
                "name": "Service Ordered 2",
                "standard_price": 10,
                "list_price": 20,
                "type": "service",
                "invoice_policy": "order",
                "uom_id": uom_hour.id,
                "uom_po_id": uom_hour.id,
                "default_code": "SERV-ORDERED2",
                "service_type": "timesheet",
                "service_tracking": "no",
                "project_id": False,  # will create a project
                "taxes_id": False,
            }
        )
        cls.product3 = Product.create(
            {
                "name": "Service delivered 3",
                "standard_price": 10,
                "list_price": 20,
                "type": "service",
                "invoice_policy": "order",
                "uom_id": uom_hour.id,
                "uom_po_id": uom_hour.id,
                "default_code": "SERV-DELI1",
                "service_type": "timesheet",
                "service_tracking": "no",
                "project_id": False,
                "taxes_id": False,
            }
        )
        cls.product4 = Product.create(
            {
                "name": "Service delivered 4",
                "standard_price": 10,
                "list_price": 20,
                "type": "service",
                "invoice_policy": "order",
                "uom_id": uom_hour.id,
                "uom_po_id": uom_hour.id,
                "default_code": "SERV-DELI2",
                "service_type": "timesheet",
                "service_tracking": "no",
                "project_id": False,
                "taxes_id": False,
            }
        )

        # Create partner
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Project Sale Order Link"}
        )

        # Create sale orders
        SaleOrder = cls.env["sale.order"].with_context(tracking_disable=True)
        SaleOrderLine = cls.env["sale.order.line"].with_context(tracking_disable=True)
        cls.sale_order1 = SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
            }
        )
        cls.so_line_order1 = SaleOrderLine.create(
            {
                "name": cls.product1.name,
                "product_id": cls.product1.id,
                "product_uom_qty": 10,
                "product_uom": cls.product1.uom_id.id,
                "price_unit": cls.product1.list_price,
                "order_id": cls.sale_order1.id,
            }
        )
        cls.sale_order2 = SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
            }
        )
        cls.so_line_order2 = SaleOrderLine.create(
            {
                "name": cls.product2.name,
                "product_id": cls.product2.id,
                "product_uom_qty": 10,
                "product_uom": cls.product2.uom_id.id,
                "price_unit": cls.product2.list_price,
                "order_id": cls.sale_order2.id,
            }
        )
        cls.sale_order3 = SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
            }
        )
        cls.so_line_order3 = SaleOrderLine.create(
            {
                "name": cls.product3.name,
                "product_id": cls.product3.id,
                "product_uom_qty": 10,
                "product_uom": cls.product3.uom_id.id,
                "price_unit": cls.product3.list_price,
                "order_id": cls.sale_order3.id,
            }
        )
        cls.sale_order4 = SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
            }
        )
        cls.so_line_order4 = SaleOrderLine.create(
            {
                "name": cls.product4.name,
                "product_id": cls.product4.id,
                "product_uom_qty": 10,
                "product_uom": cls.product4.uom_id.id,
                "price_unit": cls.product4.list_price,
                "order_id": cls.sale_order4.id,
            }
        )
        # Create employee
        cls.employee_user = cls.env["hr.employee"].create(
            {
                "name": "Employee User",
                "timesheet_cost": 15,
            }
        )
        cls.employee_manager = cls.env["hr.employee"].create(
            {
                "name": "Employee Manager",
                "timesheet_cost": 45,
            }
        )

    def test_project_sale_order_link(self):
        self.sale_order1.action_confirm()
        self.sale_order2.action_confirm()
        self.sale_order3.action_confirm()
        self.sale_order4.action_confirm()
        self.assertEqual(self.project_test.sale_order_link_ids, self.sale_order1)

        # Set sale line item in project
        self.project_test.sale_line_id = self.so_line_order2
        self.assertEqual(
            self.project_test.sale_order_link_ids, self.sale_order1 | self.sale_order2
        )

        # Set sale line item in employee map project
        self.project_test.write(
            {
                "sale_line_employee_ids": [
                    (
                        0,
                        0,
                        {
                            "employee_id": self.employee_user.id,
                            "sale_line_id": self.so_line_order3.id,
                        },
                    )
                ]
            }
        )
        self.assertEqual(
            self.project_test.sale_order_link_ids,
            self.sale_order1 | self.sale_order2 | self.sale_order3,
        )

        # Set sale line item in timesheet project
        self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "project_id": self.project_test.id,
                "unit_amount": 5,
                "employee_id": self.employee_manager.id,
                "so_line": self.so_line_order4.id,
            }
        )
        self.assertEqual(
            self.project_test.sale_order_link_ids,
            self.sale_order1 | self.sale_order2 | self.sale_order3 | self.sale_order4,
        )
