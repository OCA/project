# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date
from unittest.mock import patch

from freezegun import freeze_time

from odoo.tests import Form

from .test_forecast_line import BaseForecastRoleTest


class TestForecastRoleSales(BaseForecastRoleTest):
    def _create_sale(
        self, default_forecast_date_start, default_forecast_date_end, uom_qty=10
    ):
        self.env = self.env(user=self.user_root.id)
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.customer
            form.default_forecast_date_start = default_forecast_date_start
            form.default_forecast_date_end = default_forecast_date_end
            with form.order_line.new() as line:
                line.product_id = self.product_dev_tm
                line.product_uom_qty = uom_qty  # 1 FTE sold
                line.product_uom = self.env.ref("uom.product_uom_day")
        so = form.save()
        self.env.flush_all()
        return so

    @freeze_time("2022-01-01")
    def test_draft_sale_order_creates_negative_forecast_forecast(self):
        so = self._create_sale("2022-02-07", "2022-02-20")
        line = so.order_line[0]
        self.assertEqual(line.forecast_date_start, date(2022, 2, 7))
        self.assertEqual(line.forecast_date_end, date(2022, 2, 20))
        forecast_lines = self.ForecastLine.search(
            [
                ("sale_line_id", "=", line.id),
                ("res_model", "=", "sale.order.line"),
            ]
        )
        self.assertEqual(len(forecast_lines), 1)  # 10 days on 2022-02-01 to 2022-02-10
        self.assertEqual(forecast_lines.type, "forecast")
        self.assertEqual(
            forecast_lines.forecast_role_id,
            self.product_dev_tm.forecast_role_id,
        )
        self.assertEqual(forecast_lines.forecast_hours, -10 * 8)
        self.assertEqual(forecast_lines.cost, -10 * 8 * 75)
        self.assertEqual(forecast_lines.date_from, date(2022, 2, 1))
        self.assertEqual(forecast_lines.date_to, date(2022, 2, 28))

    @freeze_time("2022-01-01")
    def test_sale_line_unlink(self):
        so = self._create_sale("2022-02-07", "2022-02-20")
        line = so.order_line[0]
        forecast_lines = self.ForecastLine.search(
            [
                ("sale_line_id", "=", line.id),
                ("res_model", "=", "sale.order.line"),
            ]
        )
        line.unlink()
        self.assertFalse(forecast_lines.exists())

    @freeze_time("2022-01-01")
    def test_write_trigger_field_updates_forecast_lines(self):
        so = self._create_sale("2022-02-07", "2022-02-20", uom_qty=10)
        line = so.order_line[0]

        with patch.object(
            type(line),
            "_update_forecast_lines",
            autospec=True,
        ) as mock_update:
            # Call _write directly with a trigger field in the values dict.
            # 'forecast_date_end' is in _update_forecast_lines_trigger_fields().
            line._write({"forecast_date_end": date(2022, 3, 31)})

        # _update_forecast_lines must be called once when a trigger field is written
        mock_update.assert_called_once_with(line)

    @freeze_time("2022-01-01")
    def test_write_non_trigger_field_does_not_update_forecast_lines(self):
        so = self._create_sale("2022-02-07", "2022-02-20", uom_qty=10)
        line = so.order_line[0]

        with patch.object(
            type(line),
            "_update_forecast_lines",
            autospec=True,
        ) as mock_update:
            # 'customer_lead' is not a trigger field.
            line._write({"customer_lead": 5.0})

        # _update_forecast_lines must NOT be called for non-trigger fields
        mock_update.assert_not_called()

    @freeze_time("2022-01-01")
    def test_draft_sale_order_without_dates_no_forecast(self):
        """a draft sale order with no dates on the line does not create forecast"""
        so = self._create_sale("2022-02-07", False)
        line = so.order_line[0]
        self.assertEqual(line.forecast_date_start, date(2022, 2, 7))
        self.assertEqual(line.forecast_date_end, False)
        forecast_lines = self.ForecastLine.search(
            [
                ("sale_line_id", "=", line.id),
                ("res_model", "=", "sale.order.line"),
            ]
        )
        self.assertFalse(forecast_lines)

    @freeze_time("2022-01-01")
    def test_draft_sale_order_forecast_spread(self):
        so = self._create_sale("2022-02-07", "2022-04-17", uom_qty=100)

        line = so.order_line[0]
        self.assertEqual(line.forecast_date_start, date(2022, 2, 7))
        self.assertEqual(line.forecast_date_end, date(2022, 4, 17))
        forecast_lines = self.ForecastLine.search(
            [
                ("sale_line_id", "=", line.id),
                ("res_model", "=", "sale.order.line"),
            ]
        )
        self.assertEqual(len(forecast_lines), 3)
        daily_ratio = 2 * 8  # 2 FTE * 8h days
        self.assertAlmostEqual(
            forecast_lines[0].forecast_hours,
            -1 * daily_ratio * 16,  # 16 worked days between 2022 Feb 7 and Feb 28
        )
        self.assertAlmostEqual(
            forecast_lines[1].forecast_hours,
            -1 * daily_ratio * 23,  # 23 worked days in march 2022
        )
        self.assertAlmostEqual(
            forecast_lines[2].forecast_hours,
            -1 * daily_ratio * 11,  # 11 worked day between april 1 and 17 2022
        )
        self.assertEqual(
            forecast_lines.mapped("date_from"),
            [date(2022, 2, 1), date(2022, 3, 1), date(2022, 4, 1)],
        )
        self.assertEqual(
            forecast_lines.mapped("date_to"),
            [date(2022, 2, 28), date(2022, 3, 31), date(2022, 4, 30)],
        )

    @freeze_time("2022-01-01")
    def test_confirm_order_sale_order_no_forecast_line(self):
        so = self._create_sale("2022-02-14", "2022-04-14", uom_qty=60)

        so.action_confirm()
        line = so.order_line[0]
        forecast_lines = self.ForecastLine.search(
            [
                ("sale_line_id", "=", line.id),
                ("res_model", "=", "sale.order.line"),
            ]
        )
        self.assertFalse(forecast_lines)

    @freeze_time("2022-01-01")
    def test_confirm_order_sale_order_create_project_task_with_forecast_line(self):
        so = self._create_sale("2022-02-14", "2022-04-17", uom_qty=45 * 2)  # 2 FTE
        so.action_confirm()
        line = so.order_line[0]
        task = self.env["project.task"].search([("sale_line_id", "=", line.id)])
        task._update_forecast_lines()
        self.env.flush_all()
        forecast_lines = self.ForecastLine.search(
            [("res_id", "=", task.id), ("res_model", "=", "project.task")]
        )
        self.assertEqual(len(forecast_lines), 3)
        self.assertEqual(forecast_lines.mapped("forecast_role_id"), self.role_developer)
        daily_ratio = 8 * 2  # 2 FTE
        self.assertAlmostEqual(
            forecast_lines[0].forecast_hours,
            -1 * daily_ratio * 11,  # 11 working days on 2022-02-14 -> 2022-02-28
        )
        self.assertAlmostEqual(
            forecast_lines[1].forecast_hours,
            -1 * daily_ratio * 23,  # 23 working days on 2022-03-01 -> 2022-03-31
        )
        self.assertAlmostEqual(
            forecast_lines[2].forecast_hours,
            -1 * daily_ratio * 11,  # 11 working days on 2022-04-01 -> 2022-04-17
        )

    @freeze_time("2022-01-01")
    def test_timesheet_create_project_with_template_and_role_writes_tasks(self):
        # 1. Template project with a task
        template = self.ProjectProject.create({"name": "Dev Template"})
        self.ProjectTask.create({"name": "Template Task", "project_id": template.id})

        # 2. Product: project_only + template + forecast role
        product = self.ProductProduct.create(
            {
                "name": "Dev project_only (template)",
                "type": "service",
                "service_tracking": "project_only",
                "project_template_id": template.id,
                "forecast_role_id": self.role_developer.id,
                "uom_id": self.env.ref("uom.product_uom_hour").id,
                "uom_po_id": self.env.ref("uom.product_uom_hour").id,
                "standard_price": 75,
            }
        )

        forecast_start = date(2022, 2, 7)
        forecast_end = date(2022, 2, 28)

        # 3. Create and confirm a sale order
        self.env = self.env(user=self.user_root.id)
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.customer
            form.default_forecast_date_start = forecast_start
            form.default_forecast_date_end = forecast_end
            with form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = 10
                line.product_uom = self.env.ref("uom.product_uom_hour")
        so = form.save()
        so.action_confirm()
        self.env.flush_all()
        self.env.invalidate_all()

        sol = so.order_line[0]

        # 4. Find the project created from the template
        project = sol.project_id
        self.assertTrue(project, "A project must be created on confirmation")
        tasks = project.tasks
        self.assertTrue(tasks, "Template tasks must be copied into the project")

        # 5. Assert forecast fields were written to each task
        for task in tasks:
            self.assertEqual(
                task.forecast_role_id,
                self.role_developer,
                "forecast_role_id must be set from the product",
            )
            self.assertEqual(
                task.date_end.date(),
                forecast_end,
                "date_end must equal the sale line's forecast_date_end",
            )
            self.assertEqual(
                task.forecast_date_planned_start,
                forecast_start,
                "forecast_date_planned_start must equal the sale line's "
                "forecast_date_start",
            )

    @freeze_time("2022-01-01")
    def test_timesheet_create_project_without_role_skips_task_write(self):
        # 1. Template project with a task
        template = self.ProjectProject.create({"name": "Plain Template"})
        self.ProjectTask.create(
            {"name": "Plain Template Task", "project_id": template.id}
        )

        # 2. Product: project_only + template but NO forecast role
        product_no_role = self.ProductProduct.create(
            {
                "name": "Dev project_only (no role)",
                "type": "service",
                "service_tracking": "project_only",
                "project_template_id": template.id,
                # forecast_role_id intentionally omitted
                "uom_id": self.env.ref("uom.product_uom_hour").id,
                "uom_po_id": self.env.ref("uom.product_uom_hour").id,
                "standard_price": 75,
            }
        )

        # 3. Create and confirm
        self.env = self.env(user=self.user_root.id)
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.customer
            form.default_forecast_date_start = "2022-02-07"
            form.default_forecast_date_end = "2022-02-28"
            with form.order_line.new() as line:
                line.product_id = product_no_role
                line.product_uom_qty = 10
                line.product_uom = self.env.ref("uom.product_uom_hour")
        so = form.save()
        so.action_confirm()
        self.env.flush_all()
        self.env.invalidate_all()

        sol = so.order_line[0]
        project = sol.project_id
        self.assertTrue(project)
        tasks = project.tasks
        self.assertTrue(tasks, "Template tasks must still be copied")

        # Condition was False (no forecast_role_id) → forecast fields NOT set
        for task in tasks:
            self.assertFalse(
                task.forecast_role_id,
                "forecast_role_id must remain unset when product has no "
                "forecast_role_id",
            )
            self.assertFalse(
                task.date_end,
                "date_end must remain unset when the template block is skipped",
            )
