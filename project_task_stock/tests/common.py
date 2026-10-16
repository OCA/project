# Copyright 2022-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestProjectStockBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Test product A",
                "type": "consu",
                "is_storable": True,
                "standard_price": 10,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Test product B",
                "type": "consu",
                "is_storable": True,
                "standard_price": 20,
            }
        )
        cls.product_c = cls.env["product.product"].create(
            {
                "name": "Test product C",
                "type": "consu",
                "is_storable": True,
                "standard_price": 0,
            }
        )
        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "TM Test Picking Type",
                "code": "outgoing",
                "sequence_code": "TM",
                "default_location_src_id": cls.env.ref("stock.stock_location_stock").id,
                "default_location_dest_id": cls.env["stock.location"]
                .create({"name": "Destination Location for TM"})
                .id,
            }
        )
        cls.location = cls.picking_type.default_location_src_id
        cls.location_dest = cls.picking_type.default_location_dest_id
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Projects Plan"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test account",
                "plan_id": cls.plan.id,
                "company_id": False,
            },
        )
        cls.analytic_account_2 = cls.analytic_account.copy(
            {
                "name": "Test account 2",
                "plan_id": cls.plan.id,
                "company_id": False,
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Task material",
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.location.id,
                "location_dest_id": cls.location_dest.id,
                "stock_analytic_date": "1990-01-01",
                "account_id": cls.analytic_account.id,
            }
        )
        cls.stage_in_progress = cls.env["project.task.type"].create(
            {
                "name": "In Progress",
                "use_stock_moves": True,
                "project_ids": [(4, cls.project.id)],
            }
        )

        cls.stage_done = cls.env["project.task.type"].create(
            {
                "name": "Done",
                "use_stock_moves": True,
                "done_stock_moves": True,
                "project_ids": [(4, cls.project.id)],
            }
        )
        group_stock_user = "stock.group_stock_user"
        cls.basic_user = new_test_user(
            cls.env,
            login="basic-user",
            groups=f"project.group_project_user,{group_stock_user}",
        )
        new_test_user(
            cls.env,
            login="manager-user",
            groups=f"project.group_project_manager,{group_stock_user},analytic.group_analytic_accounting",
        )
        new_test_user(
            cls.env,
            login="project-task-user",
            groups="project.group_project_user,stock.group_stock_user",
        )

    @classmethod
    def _prepare_context_task(cls):
        return {
            "default_project_id": cls.project.id,
            "default_stage_id": cls.stage_in_progress.id,
            # We need to set default values according to compute store fields
            "default_location_id": cls.project.location_id.id,
            "default_location_dest_id": cls.project.location_dest_id.id,
            "default_picking_type_id": cls.project.picking_type_id.id,
        }

    @classmethod
    def _create_task(cls, products):
        task_form = Form(
            cls.env["project.task"].with_context(**cls._prepare_context_task())
        )
        task_form.name = "Test task"
        # Save task to use default_get() correctlly in stock.moves
        task_form.save()
        for product in products:
            with task_form.move_ids.new() as move_form:
                move_form.product_id = product[0]
                move_form.product_uom_qty = product[1]
        return task_form.save()
