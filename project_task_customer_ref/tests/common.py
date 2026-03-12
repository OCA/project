# Copyright 2026 ForgeFlow S.L.
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.tests import TransactionCase


class ProjectReferenceCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "taxes_id": False,
            }
        )
        cls.service_product = cls.env["product.product"].create(
            {
                "name": "Test Service",
                "type": "service",
                "taxes_id": False,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id, "product_uom_qty": 1})
                ],
            }
        )
        # sale_line_id on project drives project.sale_order_id (related field)
        cls.service_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": cls.service_product.id,
                "product_uom_qty": 1,
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "allow_billable": True,
                "sale_line_id": cls.service_line.id,
            }
        )

    def _make_task(self, **kwargs):
        """Create a project.task linked to cls.project."""
        vals = {"name": "Test Task", "project_id": self.project.id}
        vals.update(kwargs)
        return self.env["project.task"].create(vals)
