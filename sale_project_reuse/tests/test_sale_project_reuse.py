# Copyright 2026 glueckkanja AG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestSaleProjectReuse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Projects Plan"})
        cls.project = cls.env["project.project"].create(
            {
                "name": "Customer project to reuse",
                "allow_billable": True,
            }
        )
        cls.other_project = cls.env["project.project"].create(
            {
                "name": "Project chosen by hand",
                "allow_billable": True,
            }
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "is_company": True,
            }
        )
        cls.contact = cls.env["res.partner"].create(
            {
                "name": "Test Customer Contact",
                "parent_id": cls.customer.id,
            }
        )
        uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.product_reuse = cls.env["product.product"].create(
            {
                "name": "Service reusing the customer's project",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 90,
                "uom_id": uom_hour.id,
                "service_tracking": "task_in_project",
                "reuse_project": True,
            }
        )
        cls.product_no_reuse = cls.env["product.product"].create(
            {
                "name": "Service creating its own project",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 90,
                "uom_id": uom_hour.id,
                "service_tracking": "task_in_project",
            }
        )

    def _create_order(self, product, partner=None, project=None):
        order = self.env["sale.order"].create(
            {
                "partner_id": (partner or self.contact).id,
                "project_id": project.id if project else False,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "price_unit": product.list_price,
                        },
                    )
                ],
            }
        )
        return order

    def test_reuse_project_visible(self):
        product = self.product_reuse.product_tmpl_id
        self.assertTrue(
            product.reuse_project_visible,
            "Reuse Project must be visible for 'Project & Task' products",
        )
        for service_tracking in ("task_global_project", "no"):
            product.service_tracking = service_tracking
            self.assertFalse(
                product.reuse_project_visible,
                f"Reuse Project must be hidden for '{service_tracking}' products",
            )

    def test_onchange_clears_reuse_project(self):
        product = self.product_reuse.product_tmpl_id
        product.service_tracking = "no"
        product._onchange_service_tracking_reuse_project()
        self.assertFalse(
            product.reuse_project,
            "Reuse Project must be cleared when it no longer applies",
        )

    def test_onchange_sets_project_from_commercial_partner(self):
        self.customer.reuse_project_id = self.project
        with Form(self.env["sale.order"]) as order_form:
            order_form.partner_id = self.contact
            with order_form.order_line.new() as line_form:
                line_form.product_id = self.product_reuse
            self.assertEqual(
                order_form.project_id,
                self.project,
                "The project of the customer company must be proposed",
            )

    def test_confirm_sets_project_from_commercial_partner(self):
        self.customer.reuse_project_id = self.project
        project_count = self.env["project.project"].search_count([])
        order = self._create_order(self.product_reuse)
        order.action_confirm()
        self.assertEqual(
            order.project_id,
            self.project,
            "The project of the customer company must be reused",
        )
        self.assertEqual(
            self.env["project.project"].search_count([]),
            project_count,
            "No project must be generated when the project of the order is reused",
        )
        self.assertEqual(
            order.order_line.task_id.project_id,
            self.project,
            "The task must be created in the reused project",
        )

    def test_manual_project_kept(self):
        self.customer.reuse_project_id = self.project
        order = self._create_order(self.product_reuse, project=self.other_project)
        order.action_confirm()
        self.assertEqual(
            order.project_id,
            self.other_project,
            "A project set by hand must not be replaced",
        )
        self.assertEqual(
            self.customer.reuse_project_id,
            self.project,
            "The project of the customer must not be replaced",
        )
        self.assertEqual(
            order.order_line.task_id.project_id,
            self.other_project,
            "The task must be created in the project chosen on the order",
        )

    def test_partner_learns_project(self):
        order = self._create_order(self.product_reuse)
        order.action_confirm()
        self.assertTrue(
            order.project_id,
            "Confirming the order must have generated a project",
        )
        self.assertEqual(
            self.customer.reuse_project_id,
            order.project_id,
            "The project of the order must be remembered on the customer company",
        )
        # A second order for the same customer reuses the remembered project
        project_count = self.env["project.project"].search_count([])
        order_2 = self._create_order(self.product_reuse, partner=self.customer)
        order_2.action_confirm()
        self.assertEqual(
            order_2.project_id,
            order.project_id,
            "The remembered project must be reused by the following orders",
        )
        self.assertEqual(
            self.env["project.project"].search_count([]),
            project_count,
            "The following orders must not generate a project",
        )
        self.assertEqual(
            order_2.order_line.task_id.project_id,
            order.project_id,
            "The task of the following orders must land in the reused project",
        )

    def test_no_reuse_product(self):
        self.customer.reuse_project_id = self.project
        order = self._create_order(self.product_no_reuse)
        order.action_confirm()
        self.assertNotEqual(
            order.project_id,
            self.project,
            "The project of the customer must not be reused without a flagged product",
        )

    def test_no_reuse_product_generates_its_own_project(self):
        order = self._create_order(self.product_no_reuse, project=self.other_project)
        order.action_confirm()
        self.assertNotEqual(
            order.order_line.project_id,
            self.other_project,
            "Odoo must keep generating a project without a flagged product",
        )

    def test_no_reuse_product_does_not_learn(self):
        order = self._create_order(self.product_no_reuse)
        order.action_confirm()
        self.assertFalse(
            self.customer.reuse_project_id,
            "The project must not be remembered without a flagged product",
        )
