# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common
from odoo.tests.common import new_test_user


class TestProjectStockBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls.env["product.product"].create(
            {"name": "Test product A", "detailed_type": "product", "standard_price": 10}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "Test product B", "detailed_type": "product", "standard_price": 20}
        )
        cls.product_c = cls.env["product.product"].create(
            {"name": "Test product C", "detailed_type": "product", "standard_price": 0}
        )
        cls.picking_type = cls.env.ref("project_stock.stock_picking_type_tm_test")
        cls.location = cls.picking_type.default_location_src_id
        cls.location_dest = cls.picking_type.default_location_dest_id
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test account"}
        )
        cls.analytic_tag_1 = cls.env["account.analytic.tag"].create(
            {
                "name": "Test tag 1",
                "active_analytic_distribution": True,
                "analytic_distribution_ids": [
                    (0, 0, {"account_id": cls.analytic_account.id, "percentage": 100}),
                ],
            }
        )
        analytic_account_2 = cls.analytic_account.copy({"name": "Test account 2"})
        cls.analytic_tag_2 = cls.env["account.analytic.tag"].create(
            {
                "name": "Test tag 2",
                "active_analytic_distribution": True,
                "analytic_distribution_ids": [
                    (0, 0, {"account_id": cls.analytic_account.id, "percentage": 50}),
                    (0, 0, {"account_id": analytic_account_2.id, "percentage": 50}),
                ],
            }
        )
        cls.project = cls.env.ref("project_stock.project_project_tm_test")
        cls.project.analytic_account_id = cls.analytic_account
        cls.stage_in_progress = cls.env.ref("project.project_stage_1")
        cls.stage_done = cls.env.ref("project.project_stage_2")
        group_stock_user = "stock.group_stock_user"
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        new_test_user(
            cls.env,
            login="basic-user",
            groups="project.group_project_user,%s" % group_stock_user,
            context=ctx,
        )
        new_test_user(
            cls.env,
            login="manager-user",
            groups="project.group_project_manager,%s,analytic.group_analytic_accounting"
            % group_stock_user,
            context=ctx,
        )

    def _prepare_context_task(self):
        return {
            "default_project_id": self.project.id,
            "default_stage_id": self.stage_in_progress.id,
            # We need to set default values according to compute store fields
            "default_location_id": self.project.location_id.id,
            "default_location_dest_id": self.project.location_dest_id.id,
            "default_picking_type_id": self.project.picking_type_id.id,
        }

    def _create_task(self, products):
        task_form = Form(
            self.env["project.task"].with_context(**self._prepare_context_task(self))
        )
        task_form.name = "Test task"
        # Save task to use default_get() correctlly in stock.moves
        task_form.save()
        for product in products:
            with task_form.move_ids.new() as move_form:
                move_form.product_id = product[0]
                move_form.product_uom_qty = product[1]
        return task_form.save()
