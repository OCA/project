# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import Form
from odoo.tests.common import users

from .common import TestProjectStockBase


class TestProjectStock(TestProjectStockBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_stock_quant(cls, cls.product_a, cls.location, 2)
        cls._create_stock_quant(cls, cls.product_b, cls.location, 1)
        cls._create_stock_quant(cls, cls.product_c, cls.location, 1)
        cls.task = cls._create_task(cls, [(cls.product_a, 2), (cls.product_b, 1)])
        cls.move_product_a = cls.task.move_ids.filtered(
            lambda x: x.product_id == cls.product_a
        )
        cls.move_product_b = cls.task.move_ids.filtered(
            lambda x: x.product_id == cls.product_b
        )
        cls.env.ref("base.user_admin").write(
            {
                "groups_id": [
                    (4, cls.env.ref("analytic.group_analytic_accounting").id),
                    (4, cls.env.ref("analytic.group_analytic_tags").id),
                ],
            }
        )

    def _create_stock_quant(self, product, location, qty):
        self.env["stock.quant"].create(
            {"product_id": product.id, "location_id": location.id, "quantity": qty}
        )

    def test_project_task_misc(self):
        self.assertTrue(self.task.group_id)
        self.assertEqual(self.task.picking_type_id, self.picking_type)
        self.assertEqual(self.task.location_id, self.location)
        self.assertEqual(self.task.location_dest_id, self.location_dest)
        self.assertEqual(self.move_product_a.name, self.task.name)
        self.assertEqual(self.move_product_a.group_id, self.task.group_id)
        self.assertEqual(self.move_product_a.reference, self.task.name)
        self.assertEqual(self.move_product_a.location_id, self.location)
        self.assertEqual(self.move_product_a.location_dest_id, self.location_dest)
        self.assertEqual(self.move_product_a.picking_type_id, self.picking_type)
        self.assertEqual(self.move_product_a.raw_material_task_id, self.task)
        self.assertEqual(self.move_product_b.group_id, self.task.group_id)
        self.assertEqual(self.move_product_b.location_id, self.location)
        self.assertEqual(self.move_product_b.location_dest_id, self.location_dest)
        self.assertEqual(self.move_product_b.picking_type_id, self.picking_type)
        self.assertEqual(self.move_product_b.raw_material_task_id, self.task)

    def _test_task_analytic_lines_from_task(self, amount):
        self.task = self.env["project.task"].browse(self.task.id)
        # Prevent error when hr_timesheet addon is installed.
        stock_analytic_lines = self.task.sudo().stock_analytic_line_ids
        self.assertEqual(len(stock_analytic_lines), 2)
        self.assertEqual(sum(stock_analytic_lines.mapped("unit_amount")), 3)
        self.assertEqual(sum(stock_analytic_lines.mapped("amount")), amount)
        self.assertEqual(
            self.task.stock_analytic_tag_ids,
            stock_analytic_lines.mapped("tag_ids"),
        )
        self.assertIn(
            self.analytic_account,
            stock_analytic_lines.mapped("account_id"),
        )
        # Prevent incoherence when hr_timesheet addon is installed.
        if "project_id" in self.task.stock_analytic_line_ids._fields:
            self.assertFalse(self.task.stock_analytic_line_ids.project_id)

    def test_project_task_without_analytic_account(self):
        self.task = self.env["project.task"].browse(self.task.id)
        # Prevent error when hr_timesheet addon is installed.
        if "allow_timesheets" in self.task.project_id._fields:
            self.task.project_id.allow_timesheets = False
        self.task.project_id.analytic_account_id = False
        self.task.write({"stage_id": self.stage_done.id})
        self.task.action_done()
        self.assertFalse(self.task.stock_analytic_line_ids)

    @users("manager-user")
    def test_project_task_without_analytic_account_manager_user(self):
        self.test_project_task_without_analytic_account()

    def test_project_task_analytic_lines_without_tags(self):
        self.task = self.env["project.task"].browse(self.task.id)
        self.task.write({"stage_id": self.stage_done.id})
        self.task.action_done()
        self._test_task_analytic_lines_from_task(-40)
        self.assertEqual(
            fields.first(self.task.stock_analytic_line_ids).date,
            fields.Date.from_string("1990-01-01"),
        )

    @users("manager-user")
    def test_project_task_analytic_lines_without_tags_manager_user(self):
        self.test_project_task_analytic_lines_without_tags()

    def test_project_task_analytic_lines_with_tag_1(self):
        self.task = self.env["project.task"].browse(self.task.id)
        self.task.write(
            {
                "stock_analytic_date": "1991-01-01",
                "stock_analytic_tag_ids": self.analytic_tag_1.ids,
            }
        )
        self.task.write({"stage_id": self.stage_done.id})
        self.task.action_done()
        self._test_task_analytic_lines_from_task(-40)
        self.assertEqual(
            fields.first(self.task.stock_analytic_line_ids).date,
            fields.Date.from_string("1991-01-01"),
        )

    @users("manager-user")
    def test_project_task_analytic_lines_with_tag_1_manager_user(self):
        self.test_project_task_analytic_lines_with_tag_1()

    def test_project_task_analytic_lines_with_tag_2(self):
        self.task = self.env["project.task"].browse(self.task.id)
        self.task.project_id.stock_analytic_date = False
        self.task.write({"stock_analytic_tag_ids": self.analytic_tag_2.ids})
        self.task.write({"stage_id": self.stage_done.id})
        self.task.action_done()
        self._test_task_analytic_lines_from_task(-20)
        self.assertEqual(
            fields.first(self.task.stock_analytic_line_ids).date, fields.date.today()
        )

    @users("manager-user")
    def test_project_task_analytic_lines_with_tag_2_manager_user(self):
        self.test_project_task_analytic_lines_with_tag_2()

    def test_project_task_process_done(self):
        self.task = self.env["project.task"].browse(self.task.id)
        self.assertEqual(self.move_product_a.state, "draft")
        self.assertEqual(self.move_product_b.state, "draft")
        # Change task stage (auto-confirm + auto-assign)
        self.task.write({"stage_id": self.stage_done.id})
        self.assertEqual(self.move_product_a.state, "assigned")
        self.assertEqual(self.move_product_b.state, "assigned")
        self.assertEqual(self.move_product_a.reserved_availability, 2)
        self.assertEqual(self.move_product_b.reserved_availability, 1)
        self.assertTrue(self.task.stock_moves_is_locked)
        self.task.action_toggle_stock_moves_is_locked()
        self.assertFalse(self.task.stock_moves_is_locked)
        # Add new stock_move
        self.task.write({"stage_id": self.stage_in_progress.id})
        task_form = Form(self.task)
        with task_form.move_ids.new() as move_form:
            move_form.product_id = self.product_c
            move_form.product_uom_qty = 1
        task_form.save()
        move_product_c = self.task.move_ids.filtered(
            lambda x: x.product_id == self.product_c
        )
        self.assertEqual(move_product_c.group_id, self.task.group_id)
        self.assertEqual(move_product_c.state, "draft")
        self.task.action_assign()
        self.assertEqual(move_product_c.state, "assigned")
        self.task.write({"stage_id": self.stage_done.id})
        # action_done
        self.task.action_done()
        self.assertEqual(self.move_product_a.state, "done")
        self.assertEqual(self.move_product_b.state, "done")
        self.assertEqual(self.move_product_a.quantity_done, 2)
        self.assertEqual(self.move_product_b.quantity_done, 1)
        self.assertEqual(move_product_c.quantity_done, 1)

    @users("basic-user")
    def test_project_task_process_done_basic_user(self):
        self.test_project_task_process_done()

    def test_project_task_process_cancel(self):
        self.task = self.env["project.task"].browse(self.task.id)
        self.assertEqual(self.move_product_a.state, "draft")
        self.assertEqual(self.move_product_b.state, "draft")
        # Change task stage
        self.task.write({"stage_id": self.stage_done.id})
        self.assertEqual(self.move_product_a.state, "assigned")
        self.assertEqual(self.move_product_b.state, "assigned")
        # action_done
        self.task.action_done()
        self.assertEqual(self.move_product_a.state, "done")
        self.assertEqual(self.move_product_b.state, "done")
        self.assertEqual(self.move_product_a.quantity_done, 2)
        self.assertEqual(self.move_product_b.quantity_done, 1)
        self.assertTrue(self.task.sudo().stock_analytic_line_ids)
        # action_cancel
        self.task.action_cancel()
        self.assertEqual(self.move_product_a.state, "done")
        self.assertEqual(self.move_product_b.state, "done")
        self.assertEqual(self.move_product_a.quantity_done, 0)
        self.assertEqual(self.move_product_b.quantity_done, 0)
        self.assertFalse(self.task.stock_analytic_line_ids)
        quant_a = self.product_a.stock_quant_ids.filtered(
            lambda x: x.location_id == self.location
        )
        quant_b = self.product_b.stock_quant_ids.filtered(
            lambda x: x.location_id == self.location
        )
        quant_c = self.product_c.stock_quant_ids.filtered(
            lambda x: x.location_id == self.location
        )
        self.assertEqual(quant_a.quantity, 2)
        self.assertEqual(quant_b.quantity, 1)
        self.assertEqual(quant_c.quantity, 1)

    @users("manager-user")
    def test_project_task_process_cancel_manager_user(self):
        self.test_project_task_process_cancel()

    def test_project_task_process_unreserve(self):
        self.task = self.env["project.task"].browse(self.task.id)
        self.assertEqual(self.move_product_a.state, "draft")
        self.assertEqual(self.move_product_b.state, "draft")
        # Change task stage (auto-confirm + auto-assign)
        self.task.write({"stage_id": self.stage_done.id})
        self.assertTrue(self.move_product_a.move_line_ids)
        self.assertEqual(self.move_product_a.move_line_ids.task_id, self.task)
        self.assertEqual(self.move_product_a.state, "assigned")
        self.assertEqual(self.move_product_b.state, "assigned")
        self.assertEqual(self.move_product_a.reserved_availability, 2)
        self.assertEqual(self.move_product_b.reserved_availability, 1)
        self.assertTrue(self.task.unreserve_visible)
        # button_unreserve
        self.task.button_unreserve()
        self.assertEqual(self.move_product_a.state, "confirmed")
        self.assertEqual(self.move_product_b.state, "confirmed")
        self.assertEqual(self.move_product_a.reserved_availability, 0)
        self.assertEqual(self.move_product_b.reserved_availability, 0)
        self.assertFalse(self.task.unreserve_visible)

    @users("basic-user")
    def test_project_task_process_unreserve_basic_user(self):
        self.test_project_task_process_unreserve()

    def test_project_task_action_cancel(self):
        self.assertTrue(self.env["project.task"].browse(self.task.id).action_cancel())

    @users("basic-user")
    def test_project_task_action_cancel_basic_user(self):
        self.test_project_task_action_cancel()

    def test_project_task_action_done(self):
        self.task = self.env["project.task"].browse(self.task.id)
        self.task.write({"stage_id": self.stage_done.id})
        self.task.action_done()
        self.assertTrue(self.task.sudo().stock_analytic_line_ids)

    @users("basic-user")
    def test_project_task_action_done_basic_user(self):
        self.test_project_task_action_done()

    def test_project_task_unlink(self):
        self.assertTrue(self.env["project.task"].browse(self.task.id).unlink())

    @users("basic-user")
    def test_project_task_unlink_basic_user(self):
        self.test_project_task_unlink()
