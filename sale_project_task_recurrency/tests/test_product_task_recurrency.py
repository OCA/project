# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from freezegun import freeze_time

from odoo import fields
from odoo.tests import new_test_user
from odoo.tests.common import users
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestProductTaskRecurrency(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Task = cls.env["project.task"]
        cls.Product = cls.env["product.product"]
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleLine = cls.env["sale.order.line"]
        cls.env.user.tz = "UTC"
        cls.user = new_test_user(
            cls.env,
            login="test-user",
            groups="sales_team.group_sale_salesman,project.group_project_recurring_tasks",
            tz=cls.env.user.tz,
        )
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.project_global = cls.env["project.project"].create(
            {"name": "Global Project", "allow_billable": True}
        )
        product_vals = {
            "name": "Service",
            "type": "service",
            "uom_id": cls.uom_hour.id,
            "uom_po_id": cls.uom_hour.id,
            "service_type": "manual",
            "service_tracking": "no",
        }
        cls.service_no_task = cls.Product.create(product_vals)
        cls.service_task = cls.Product.create(
            dict(
                product_vals,
                name="Service task",
                service_tracking="task_global_project",
                project_id=cls.project_global.id,
            )
        )
        cls.service_task_recurrency = cls.Product.create(
            dict(
                product_vals,
                name="Service task recurrency",
                service_tracking="task_global_project",
                project_id=cls.project_global.id,
                recurring_task=True,
                task_repeat_interval=1,
                task_repeat_unit="day",
            )
        )
        cls.sale_order = cls.SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
            }
        )
        cls.sol_no_task = cls.SaleLine.create(
            {
                "product_id": cls.service_no_task.id,
                "product_uom_qty": 10,
                "order_id": cls.sale_order.id,
            }
        )
        cls.sol_task = cls.SaleLine.create(
            {
                "product_id": cls.service_task.id,
                "product_uom_qty": 10,
                "order_id": cls.sale_order.id,
            }
        )
        cls.sol_task_recurrency = cls.SaleLine.create(
            {
                "product_id": cls.service_task_recurrency.id,
                "product_uom_qty": 10,
                "order_id": cls.sale_order.id,
            }
        )

    @mute_logger("odoo.models.unlink")
    def _reprocess_sale_order(self):
        self.sale_order.tasks_ids.unlink()
        self.sale_order._action_cancel()
        self.sale_order.action_draft()
        self.sale_order.action_confirm()

    def _get_last_task(self, task):
        last_task_id = task.recurrence_id._get_last_task_id_per_recurrence_id()[
            task.recurrence_id.id
        ]
        return self.Task.browse(last_task_id)

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_day(self):
        """Every 1 day forever"""
        self.service_task_recurrency.task_repeat_unit = "day"
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 1)
        self.assertEqual(task.repeat_unit, "day")
        self.assertEqual(task.repeat_type, "forever")
        self.assertFalse(task.repeat_until)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2024-11-16")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_week(self):
        """Every 1 week forever"""
        self.service_task_recurrency.task_repeat_unit = "week"
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 1)
        self.assertEqual(task.repeat_unit, "week")
        self.assertEqual(task.repeat_type, "forever")
        self.assertFalse(task.repeat_until)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2024-11-22")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_month(self):
        """Every 1 month forever"""
        self.service_task_recurrency.task_repeat_unit = "month"
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 1)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.repeat_type, "forever")
        self.assertFalse(task.repeat_until)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2024-12-15")
        )
        # start_date_method = "start_this"
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2024-12-01")
        )
        # start_date_method = "end_this"
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-30")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2024-12-30")
        )
        # start_date_method = "start_next"
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-12-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-01-01")
        )
        # start_date_method = "end_next"
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-12-31")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-01-31")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_3_month(self):
        """Every 3 month forever"""
        self.service_task_recurrency.task_repeat_unit = "month"
        self.service_task_recurrency.task_repeat_interval = 3
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 3)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.repeat_type, "forever")
        self.assertFalse(task.repeat_until)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-02-15")
        )
        # start_date_method = "start_this"
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-02-01")
        )
        # start_date_method = "end_this"
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-30")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-02-28")
        )
        # start_date_method = "start_next"
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-02-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-05-01")
        )
        # start_date_method = "end_next"
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-02-28")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        # date is 28/05 instead 31/05
        # because Odoo in roject.task not force to end of month, only added month
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-05-28")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_quarter(self):
        """Every 1 quarter forever"""
        self.service_task_recurrency.task_repeat_unit = "quarter"
        self.service_task_recurrency.task_repeat_interval = 1
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        # quarter is 3 months
        self.assertEqual(task.repeat_interval, 3)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.repeat_type, "forever")
        self.assertFalse(task.repeat_until)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-02-15")
        )
        # start_date_method = "start_this"
        # on November, the quarter start on October
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-10-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-01-01")
        )
        # start_date_method = "end_this"
        # on November, the quarter ends on December
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-12-31")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-03-31")
        )
        # start_date_method = "start_next"
        # on November, the next quarter starts on January
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-01-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-04-01")
        )
        # start_date_method = "end_next"
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-03-31")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-06-30")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_semester(self):
        """Every 1 quarter forever"""
        self.service_task_recurrency.task_repeat_unit = "semester"
        self.service_task_recurrency.task_repeat_interval = 1
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        # semester is 6 months
        self.assertEqual(task.repeat_interval, 6)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.repeat_type, "forever")
        self.assertFalse(task.repeat_until)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-05-15")
        )
        # start_date_method = "start_this"
        # on November, the semester start on July
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-07-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-01-01")
        )
        # start_date_method = "end_this"
        # on November, the semester ends on December
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-12-31")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-06-30")
        )
        # start_date_method = "start_next"
        # on November, the next semester starts on January
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-01-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-07-01")
        )
        # start_date_method = "end_next"
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-06-30")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-12-30")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_year(self):
        """Every 1 year forever"""
        self.service_task_recurrency.task_repeat_unit = "year"
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 1)
        self.assertEqual(task.repeat_unit, "year")
        self.assertEqual(task.repeat_type, "forever")
        self.assertFalse(task.repeat_until)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-11-15")
        )
        # start_date_method = "start_this"
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-01-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-01-01")
        )
        # start_date_method = "end_this"
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-12-31")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-12-31")
        )
        # start_date_method = "start_next"
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-01-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2026-01-01")
        )
        # start_date_method = "end_next"
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-12-31")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2026-12-31")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_3_year(self):
        """Every 3 year forever"""
        self.service_task_recurrency.task_repeat_unit = "year"
        self.service_task_recurrency.task_repeat_interval = 3
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 3)
        self.assertEqual(task.repeat_unit, "year")
        self.assertEqual(task.repeat_type, "forever")
        self.assertFalse(task.repeat_until)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2027-11-15")
        )
        # start_date_method = "start_this"
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-01-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2027-01-01")
        )
        # start_date_method = "end_this"
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-12-31")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2027-12-31")
        )
        # start_date_method = "start_next"
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2027-01-01")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2030-01-01")
        )
        # start_date_method = "end_next"
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2027-12-31")
        )
        self.assertEqual(task.recurring_count, 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2030-12-31")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_month_repeat_until(self):
        """Every 3 months until 2025-06-15"""
        self.service_task_recurrency.task_repeat_interval = 3
        self.service_task_recurrency.task_repeat_unit = "month"
        self.service_task_recurrency.task_repeat_type = "until"
        self.service_task_recurrency.task_repeat_until = fields.Date.from_string(
            "2025-06-15"
        )
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 3)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.repeat_type, "until")
        self.assertEqual(task.repeat_until, fields.Date.from_string("2025-06-15"))
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        # generate a new task
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2025-06-15"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-02-15")
        )
        # generate a new task
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 3)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2025-06-15"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-05-15")
        )
        # no generate a new task
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 3)

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_month_repeat_number(self):
        """Every 3 months, 3 repeats, until 2025-08-15"""
        self.service_task_recurrency.task_repeat_interval = 3
        self.service_task_recurrency.task_repeat_unit = "month"
        self.service_task_recurrency.task_repeat_type = "repeat"
        self.service_task_recurrency.task_repeat_number = 3
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 3)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.repeat_type, "until")
        self.assertEqual(task.repeat_until, fields.Date.from_string("2025-08-15"))
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        # generate a new task(repeat 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2025-08-15"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-02-15")
        )
        # generate a new task(repeat 2)
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 3)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2025-08-15"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-05-15")
        )
        # generate a new task(repeat 3)
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 4)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2025-08-15"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-08-15")
        )
        # no generate a new task
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 4)

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_year_repeat_until(self):
        """Every 1 years until 2026-12-31"""
        self.service_task_recurrency.task_repeat_interval = 1
        self.service_task_recurrency.task_repeat_unit = "year"
        self.service_task_recurrency.task_repeat_type = "until"
        self.service_task_recurrency.task_repeat_until = fields.Date.from_string(
            "2026-12-31"
        )
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 1)
        self.assertEqual(task.repeat_unit, "year")
        self.assertEqual(task.repeat_type, "until")
        self.assertEqual(task.repeat_until, fields.Date.from_string("2026-12-31"))
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        # generate a new task
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2026-12-31"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-11-15")
        )
        # generate a new task
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 3)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2026-12-31"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2026-11-15")
        )
        # no generate a new task
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 3)

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_year_repeat_number(self):
        """Every 1 year, 3 repeats, until 2027-11-15"""
        self.service_task_recurrency.task_repeat_interval = 1
        self.service_task_recurrency.task_repeat_unit = "year"
        self.service_task_recurrency.task_repeat_type = "repeat"
        self.service_task_recurrency.task_repeat_number = 3
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 1)
        self.assertEqual(task.repeat_unit, "year")
        self.assertEqual(task.repeat_type, "until")
        self.assertEqual(task.repeat_until, fields.Date.from_string("2027-11-15"))
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        self.assertEqual(task.recurring_count, 1)
        # generate a new task(repeat 1)
        task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 2)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2027-11-15"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2025-11-15")
        )
        # generate a new task(repeat 2)
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 3)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2027-11-15"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2026-11-15")
        )
        # generate a new task(repeat 3)
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 4)
        last_task = self._get_last_task(task)
        self.assertEqual(last_task.repeat_until, fields.Date.from_string("2027-11-15"))
        self.assertEqual(
            last_task.date_deadline.date(), fields.Date.from_string("2027-11-15")
        )
        # no generate a new task
        last_task.state = "1_done"
        task.invalidate_recordset(["recurring_count"])
        self.assertEqual(task.recurring_count, 4)

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_year_force_month(self):
        """Every 1 year, force month to July"""
        self.service_task_recurrency.task_repeat_interval = 1
        self.service_task_recurrency.task_repeat_unit = "year"
        self.service_task_recurrency.task_force_month = "6"
        self.service_task_recurrency.task_repeat_type = "forever"
        self.sale_order.action_confirm()
        self.assertFalse(self.sol_no_task.task_id)
        self.assertFalse(self.sol_task.task_id.recurring_task)
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 1)
        self.assertEqual(task.repeat_unit, "year")
        self.assertEqual(task.repeat_type, "forever")
        self.assertEqual(task.recurring_count, 1)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-06-15")
        )
        # start_this
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-06-01")
        )
        # end_this
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-06-30")
        )
        # start_next
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-06-01")
        )
        # end_next
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-06-30")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_quarter_force_month(self):
        # Force month to firts month of quarter: January, April, July, October
        self.service_task_recurrency.task_repeat_interval = 1
        self.service_task_recurrency.task_repeat_unit = "quarter"
        self.service_task_recurrency.task_force_month_quarter = "1"
        self.service_task_recurrency.task_repeat_type = "forever"
        self.sale_order.action_confirm()
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 3)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.repeat_type, "forever")
        self.assertEqual(task.recurring_count, 1)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-10-15")
        )
        # start_this
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-10-01")
        )
        # end_this
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-10-31")
        )
        # start_next
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-01-01")
        )
        # end_next
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-01-31")
        )
        # Force month to second month of quarter: February, May, August, November
        self.service_task_recurrency.task_force_month_quarter = "2"
        self.service_task_recurrency.task_start_date_method = "current_date"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 3)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.recurring_count, 1)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-15")
        )
        # start_this
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-01")
        )
        # end_this
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-11-30")
        )
        # start_next
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-02-01")
        )
        # end_next
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-02-28")
        )
        # Force month to third month of quarter: March, June, September, December
        self.service_task_recurrency.task_force_month_quarter = "3"
        self.service_task_recurrency.task_start_date_method = "current_date"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 3)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.recurring_count, 1)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-12-15")
        )
        # start_this
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-12-01")
        )
        # end_this
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-12-31")
        )
        # start_next
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-03-01")
        )
        # end_next
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-03-31")
        )

    @users("test-user")
    @freeze_time("2024-11-15")
    def test_task_recurrency_semester_force_month(self):
        # Force month to second month of semester
        self.service_task_recurrency.task_repeat_interval = 1
        self.service_task_recurrency.task_repeat_unit = "semester"
        self.service_task_recurrency.task_force_month_semester = "2"
        self.service_task_recurrency.task_repeat_type = "forever"
        self.sale_order.action_confirm()
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.repeat_interval, 6)
        self.assertEqual(task.repeat_unit, "month")
        self.assertEqual(task.repeat_type, "forever")
        self.assertEqual(task.recurring_count, 1)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-08-15")
        )
        # start_this
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-08-01")
        )
        # end_this
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-08-31")
        )
        # start_next
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-02-01")
        )
        # end_next
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-02-28")
        )
        # Force month to four month of semester
        self.service_task_recurrency.task_force_month_semester = "4"
        self.service_task_recurrency.task_start_date_method = "current_date"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertTrue(task.recurring_task)
        self.assertEqual(task.recurring_count, 1)
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-10-15")
        )
        # start_this
        self.service_task_recurrency.task_start_date_method = "start_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-10-01")
        )
        # end_this
        self.service_task_recurrency.task_start_date_method = "end_this"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2024-10-31")
        )
        # start_next
        self.service_task_recurrency.task_start_date_method = "start_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-04-01")
        )
        # end_next
        self.service_task_recurrency.task_start_date_method = "end_next"
        self._reprocess_sale_order()
        task = self.sol_task_recurrency.task_id
        self.assertEqual(
            task.date_deadline.date(), fields.Date.from_string("2025-04-30")
        )
