import logging

from freezegun import freeze_time

from .test_forecast_line import BaseForecastRoleTest

_logger = logging.getLogger(__name__)


class TestProjectTask(BaseForecastRoleTest):
    def test_task_onchange_user(self):
        """Test task.onchange_user_ids."""

        project = self.env["project.project"].create({"name": "Test Project Onchange"})
        task = self.env["project.task"].new(
            {
                "name": "Test Task Onchange",
                "project_id": project.id,
                "forecast_role_id": False,
            }
        )
        task.user_ids = [(4, self.user_consultant.id)]
        self.env.flush_all()

        # Manually trigger the onchange logic
        task.onchange_user_ids()

        self.assertEqual(task.forecast_role_id.id, self.role_consultant.id)
        # Verify that it doesn't overwrite if already set
        task.onchange_user_ids()
        self.env.flush_all()
        self.assertEqual(task.forecast_role_id.id, self.role_consultant.id)

    def test_task_onchange_user_clear_users_clears_role(self):
        """Removing all users from a task must clear forecast_role_id."""
        project = self.env["project.project"].create({"name": "Test Project ClearUser"})
        task = self.env["project.task"].new(
            {
                "name": "Test Task ClearUser",
                "project_id": project.id,
                "forecast_role_id": False,
            }
        )
        # Assign a user → role gets set via onchange
        task.user_ids = [(4, self.user_consultant.id)]
        task.onchange_user_ids()
        self.assertEqual(task.forecast_role_id.id, self.role_consultant.id)

        # Remove all users → forecast_role_id must be cleared
        task.user_ids = [(5,)]
        task.onchange_user_ids()
        self.assertFalse(
            task.forecast_role_id,
            "forecast_role_id must be cleared when user_ids is empty",
        )

    def test_task_quick_update_forecast(self):
        """Test _quick_update_forecast_lines method logic"""
        project = self.ProjectProject.create({"name": "TestProjectQuick"})
        project.stage_id = self.env.ref("project.project_project_stage_1")

        task_vals = {
            "name": "Test Task Quick",
            "project_id": project.id,
            "forecast_role_id": self.role_consultant.id,
            "forecast_date_planned_start": "2022-02-14",
            "forecast_date_planned_end": "2022-02-14",
            "allocated_hours": 8,
            "remaining_hours": 8,
        }
        task = self.ProjectTask.create(task_vals)
        # Force line generation #noqa : E501
        task._update_forecast_lines()

        forecast_lines = self.env["forecast.line"].search(
            [("res_id", "=", task.id), ("res_model", "=", "project.task")]
        )
        self.assertEqual(len(forecast_lines), 1)
        self.assertEqual(forecast_lines[0].forecast_hours, -8.0)

        # Trigger quick update by changing remaining_hours
        task.write({"remaining_hours": 4.0})
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(forecast_lines[0].forecast_hours, -4.0)

        # Test ratio with multiple lines (if we had them, but here it's 1:1)
        task.write({"remaining_hours": 2.0})
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(forecast_lines[0].forecast_hours, -2.0)

    @freeze_time("2022-02-14 12:00:00")
    def test_quick_update_fallback_when_no_forecast_lines(self):
        """When no forecast lines exist for a task, _quick_update_forecast_lines
        must fall back to _update_forecast_lines() and create them.
        """
        project = self.ProjectProject.create({"name": "TestQuickFallback"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        task = self.ProjectTask.create(
            {
                "name": "No Lines Task",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )
        task.user_ids = self.user_consultant

        # Confirm: no forecast lines exist yet
        lines_before = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertFalse(lines_before)

        # Call _quick_update_forecast_lines → no lines exist → fallback
        task._quick_update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        lines_after = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertTrue(
            lines_after,
            "_quick_update_forecast_lines must fall back to "
            "_update_forecast_lines when no forecast lines exist",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_quick_update_fallback_when_total_forecast_zero(self):
        """When forecast lines exist but total_forecast is zero,
        _quick_update_forecast_lines must fall back to
        _update_forecast_lines() (ratio division would be undefined).
        """
        project = self.ProjectProject.create({"name": "TestQuickZero"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        task = self.ProjectTask.create(
            {
                "name": "Zero Total Task",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )
        task.user_ids = self.user_consultant
        task._update_forecast_lines()
        self.env.flush_all()

        lines = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertTrue(lines)

        # Force total_forecast to zero by zeroing out all lines
        for line in lines:
            line.forecast_hours = 0.0
        self.env.flush_all()

        # Call _quick_update → total_forecast is 0 → fallback
        task._quick_update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        lines_after = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertTrue(
            lines_after,
            "_quick_update_forecast_lines must fall back when total is zero",
        )

    # ------------------------------------------------------------------
    # Tests for project.task._write (models/project_task.py L56-L62)
    # ------------------------------------------------------------------

    @freeze_time("2022-02-14 12:00:00")
    def test_write_forecast_recomputation_trigger_calls_update_forecast_lines(self):
        """when forecast_recomputation_trigger is stored, _update_forecast_lines
        must be invoked and regenerate the task's forecast lines."""
        project = self.ProjectProject.create({"name": "TestWriteTrigger"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        task = self.ProjectTask.create(
            {
                "name": "Write Trigger Task",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )
        task.user_ids = self.user_consultant
        # Generate initial forecast lines
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        lines_before = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertTrue(lines_before, "Forecast lines should exist before the write")

        # Changing a trigger field (e.g. forecast_date_planned_end) causes the
        # computed field forecast_recomputation_trigger to be recomputed and
        # stored via _write, which must call _update_forecast_lines().
        task.write({"forecast_date_planned_end": "2022-02-15"})
        self.env.flush_all()
        self.env.invalidate_all()

        lines_after = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        # Lines should still exist (regenerated) and reflect the new date range
        self.assertTrue(
            lines_after,
            "_update_forecast_lines should have regenerated forecast lines",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_write_remaining_hours_calls_quick_update_forecast_lines(self):
        """when remaining_hours changes (without a trigger-field change),
        _quick_update_forecast_lines must scale existing lines proportionally."""
        project = self.ProjectProject.create({"name": "TestWriteRemainingHours"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        task = self.ProjectTask.create(
            {
                "name": "Quick Update Task",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )
        task.user_ids = self.user_consultant
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        lines = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertEqual(len(lines), 1)
        self.assertAlmostEqual(lines[0].forecast_hours, -8.0)

        # Directly call _write with remaining_hours to simulate ORM internal path
        task._write({"remaining_hours": 4.0})
        self.env.flush_all()
        self.env.invalidate_all()

        # _quick_update_forecast_lines applies ratio: 4 / 8 = 0.5 → -4.0 h
        self.assertAlmostEqual(
            lines[0].forecast_hours,
            -4.0,
            msg="_quick_update_forecast_lines should scale forecast_hours by ratio",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_write_unrelated_field_leaves_forecast_lines_unchanged(self):
        """writing a field that is neither forecast_recomputation_trigger
        nor remaining_hours must leave forecast lines completely untouched."""
        project = self.ProjectProject.create({"name": "TestWriteUnrelated"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        task = self.ProjectTask.create(
            {
                "name": "Unrelated Write Task",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )
        task.user_ids = self.user_consultant
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        lines_before = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        hours_before = lines_before.mapped("forecast_hours")

        # Write a field that does not trigger any forecast logic
        task._write({"description": "Some description update"})
        self.env.flush_all()
        self.env.invalidate_all()

        lines_after = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertEqual(
            lines_before.ids,
            lines_after.ids,
            "Forecast line records must not change for an unrelated field write",
        )
        self.assertEqual(
            hours_before,
            lines_after.mapped("forecast_hours"),
            "Forecast hours must remain unchanged for an unrelated field write",
        )

    # ------------------------------------------------------------------
    # Tests for project.task._update_forecast_lines
    # Covers: cleanup of orphan lines (task_with_lines_to_clean)
    #         and creation of new lines (ForecastLine.create(forecast_vals))
    # ------------------------------------------------------------------

    @freeze_time("2022-02-14 12:00:00")
    def test_update_forecast_lines_cleans_orphan_lines_when_task_loses_forecast(self):
        """forecast lines for a task that no longer qualifies for a
        forecast must be unlinked when _update_forecast_lines is called.

        A task is disqualified from having a forecast when it no longer meets
        _should_have_forecast() (e.g. forecast_role_id is removed).
        """
        project = self.ProjectProject.create({"name": "TestCleanOrphan"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        task = self.ProjectTask.create(
            {
                "name": "Orphan Cleanup Task",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )
        task.user_ids = self.user_consultant
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        lines = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertTrue(lines, "Forecast lines should exist before disqualification")

        # Remove the forecast role → task._should_have_forecast() returns False
        # _update_forecast_lines adds it to task_with_lines_to_clean and unlinks
        task.write({"forecast_role_id": False})
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        orphan_lines = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertFalse(
            orphan_lines,
            "All forecast lines must be deleted when the task no longer qualifies",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_update_forecast_lines_creates_new_lines_for_qualifying_task(self):
        """forecast_vals collected during the loop must be persisted via
        ForecastLine.create(), producing the expected number of new records.
        """
        project = self.ProjectProject.create({"name": "TestCreateLines"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        task = self.ProjectTask.create(
            {
                "name": "New Lines Task",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )
        task.user_ids = self.user_consultant

        # No lines should exist yet
        lines_before = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertFalse(lines_before, "No forecast lines should exist before the call")

        created = task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        lines_after = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        self.assertTrue(
            lines_after,
            "ForecastLine.create(forecast_vals) should have created at least one line",
        )
        # _update_forecast_lines returns the created lines
        self.assertTrue(
            created,
            "_update_forecast_lines should return the newly created forecast lines",
        )
        self.assertEqual(
            lines_after.mapped("forecast_hours"),
            [-8.0],
            "Created line should carry the full remaining_hours as a negative value",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_update_forecast_lines_no_cleanup_when_all_tasks_qualify(self):
        """when every task in the recordset still qualifies for a
        forecast, task_with_lines_to_clean stays empty and no unlink is called.

        We verify this by asserting that existing lines are preserved (not
        deleted) and that the creation path still produces lines.
        """
        project = self.ProjectProject.create({"name": "TestNoCleanup"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        task = self.ProjectTask.create(
            {
                "name": "No Cleanup Task",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )
        task.user_ids = self.user_consultant
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        lines_first_run = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        ids_first_run = set(lines_first_run.ids)
        self.assertTrue(ids_first_run)

        # Call again without changing anything: task still qualifies, so
        # task_with_lines_to_clean must remain empty → no unlink occurs.
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()

        lines_second_run = self.env["forecast.line"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", task.id)]
        )
        # Original lines must still be present (not wiped by an erroneous cleanup)
        surviving_ids = ids_first_run & set(lines_second_run.ids)  # noqa : E501
        self.assertTrue(
            surviving_ids,
            "No forecast lines should have been deleted when task_with_lines_to_clean is empty",  # noqa : E501
        )

    # ------------------------------------------------------------------
    # Tests for project.task._should_have_forecast
    # ------------------------------------------------------------------

    def _make_qualifying_task(self, name="ShouldHaveTask"):
        """Helper: create a task that passes all _should_have_forecast checks."""
        project = self.ProjectProject.create({"name": f"ShouldHaveProject-{name}"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        self.env.flush_all()
        task = self.ProjectTask.create(
            {
                "name": name,
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )
        return task

    def test_should_have_forecast_ensure_one_raises_on_multi_record(self):
        """ensure_one() must raise when called on a multi-record set."""
        with freeze_time("2022-02-14 12:00:00"):
            task_a = self._make_qualifying_task("EnsureOneA")
            task_b = self._make_qualifying_task("EnsureOneB")
        multi = task_a | task_b
        with self.assertRaises(ValueError):
            multi._should_have_forecast()

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_returns_false_when_no_forecast_role(self):
        """missing forecast_role_id → False immediately."""
        task = self._make_qualifying_task("NoRole")
        task.forecast_role_id = False
        self.assertFalse(
            task._should_have_forecast(),
            "_should_have_forecast must return False when forecast_role_id is unset",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_no_project_falls_through_to_date_hours_checks(self):
        """the elif-not-project_id branch only logs; it does NOT
        return False. Execution falls through to the date/hours guards, and
        because those pass the method returns True."""
        task = self._make_qualifying_task("NoProject")
        task.project_id = False
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertTrue(
            task._should_have_forecast(),
            "With no project but valid dates/hours the fall-through should return True",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_returns_false_when_project_stage_has_no_forecast_type(
        self,
    ):
        """Project has a stage but forecast_line_type is falsy → False."""
        stage_no_forecast = self.env["project.project.stage"].create(
            {"name": "NoForecastStage", "forecast_line_type": False}
        )
        project = self.ProjectProject.create({"name": "ShouldHaveNoStageForecast"})
        project.stage_id = stage_no_forecast
        self.env.flush_all()
        task = self.ProjectTask.create(
            {
                "name": "StageForecastFalse",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )  # noqa : E501
        self.assertFalse(
            task._should_have_forecast(),
            "_should_have_forecast must return False when stage has no forecast_line_type",  # noqa : E501
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_returns_false_when_no_planned_start_date(self):
        """Missing forecast_date_planned_start → False."""
        task = self._make_qualifying_task("NoStartDate")
        task.forecast_date_planned_start = False
        self.env.flush_all()  # noqa : E501
        self.assertFalse(
            task._should_have_forecast(),
            "_should_have_forecast must return False when planned start date is missing",  # noqa : E501
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_returns_false_when_no_planned_end_date(self):
        """Missing forecast_date_planned_end → False."""
        task = self._make_qualifying_task("NoEndDate")
        task.forecast_date_planned_end = False
        self.env.flush_all()
        self.assertFalse(
            task._should_have_forecast(),
            "_should_have_forecast must return False when planned end date is missing",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_returns_false_when_remaining_hours_zero(self):
        """Remaining_hours == 0 → False."""
        task = self._make_qualifying_task("ZeroHours")
        task.remaining_hours = 0
        self.env.flush_all()
        self.assertFalse(
            task._should_have_forecast(),
            "_should_have_forecast must return False when remaining_hours is 0",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_returns_false_when_remaining_hours_negative(self):
        """Remaining_hours < 0 → False."""
        task = self._make_qualifying_task("NegativeHours")
        task.remaining_hours = -1
        self.env.flush_all()
        self.assertFalse(
            task._should_have_forecast(),
            "_should_have_forecast must return False when remaining_hours is negative",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_returns_true_for_fully_qualified_task(self):
        """All conditions met → True (happy path)."""
        task = self._make_qualifying_task("HappyPath")
        self.assertTrue(
            task._should_have_forecast(),
            "_should_have_forecast must return True when all conditions are satisfied",
        )

    def _make_task_with_sale_line(self, name, so_state="draft", project_stage_id=False):
        """Helper: create a task linked to a sale order line.

        The project deliberately has *no* stage so that
        _should_have_forecast reaches the elif self.sale_line_id branch.
        so_state can be 'draft', 'sale', or 'cancel'.

        A plain consumable product is used for the sale line deliberately so
        that Odoo's sale/project integration does NOT auto-confirm the SO when
        the task is created (service_tracking products trigger that behaviour).
        """
        # Project with no stage → stage_id is False
        project = self.ProjectProject.create(
            {"name": f"SaleLinePrj-{name}", "stage_id": project_stage_id}
        )
        self.env.flush_all()

        # Plain consumable — no service_tracking, so SO stays in draft
        plain_product = self.env["product.product"].create(
            {
                "name": f"plain-product-{name}",
                "type": "service",
                "list_price": 10,
                "standard_price": 5,
            }
        )

        partner = self.env.ref("base.res_partner_1")
        sale_order = self.env["sale.order"].create({"partner_id": partner.id})
        sale_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": plain_product.id,
                "product_uom_qty": 8,
                "price_unit": 10,
            }
        )
        task = self.ProjectTask.create(
            {
                "name": name,
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "sale_line_id": sale_line.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": 8,
                "remaining_hours": 8,
            }
        )

        self.env.flush_all()  # noqa : E501
        # After task creation, the SO might be auto-confirmed by Odoo depending on default settings. #noqa : E501
        # So we force the SO to reach the expected state using standard actions.
        if so_state == "sale":
            if sale_order.state != "sale":
                sale_order.action_confirm()
        elif so_state == "cancel":
            if sale_order.state != "cancel":
                if sale_order.state == "draft":
                    sale_order.action_cancel()
                else:
                    sale_order.with_context(disable_cancel_warning=True).action_cancel()
        elif so_state == "draft":
            if sale_order.state != "draft":
                sale_order.with_context(disable_cancel_warning=True).action_cancel()
                sale_order.action_draft()

        self.env.flush_all()
        self.env.invalidate_all()

        return task, sale_order

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_sale_line_cancelled_returns_false(self):
        """A task linked to a cancelled
        sale order must return False from _should_have_forecast."""
        task, so = self._make_task_with_sale_line("SaleLineCancel", so_state="cancel")
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(so.state, "cancel")
        self.assertFalse(
            task._should_have_forecast(),
            "Should return False when the linked sale order is cancelled",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_sale_line_confirmed_returns_true(self):
        """A task linked to a confirmed
        sale order must return True from _should_have_forecast."""
        task, so = self._make_task_with_sale_line("SaleLineConfirmed", so_state="sale")
        self.assertEqual(so.state, "sale")
        self.assertTrue(
            task._should_have_forecast(),
            "Should return True when the linked sale order is confirmed",
        )

    @freeze_time("2022-02-14 12:00:00")
    def test_should_have_forecast_sale_line_draft_returns_false(self):
        """A task linked to a draft sale order
        must return False from _should_have_forecast."""
        task, so = self._make_task_with_sale_line("SaleLineDraft", so_state="draft")
        self.assertEqual(so.state, "draft")
        self.assertFalse(
            task._should_have_forecast(),
            "Should return False when the linked sale order is in draft state",
        )

    def test_set_forecast_type(self):
        # Condition 1: Project with stage ID
        task, so = self._make_task_with_sale_line(
            "SaleLineDraft", so_state="draft", project_stage_id=1
        )  # Stage ID: 1 --> To Do stage
        forecast_type = task.set_forecast_type()
        self.assertEqual(forecast_type, "forecast")

        # Condition 2: Task with SO line in sale state
        task_2, so = self._make_task_with_sale_line(
            "SaleLineConfirm", so_state="sale", project_stage_id=False
        )
        task_2.project_id.stage_id = False
        forecast_type = task_2.set_forecast_type()
        self.env.flush_all()
        self.assertEqual(forecast_type, "confirmed")

        # Condition 3: Task with SO line in draft state → bare return (None)
        task_3, so_3 = self._make_task_with_sale_line(
            "SaleLineDraftReturn", so_state="draft", project_stage_id=False
        )
        task_3.project_id.stage_id = False
        forecast_type = task_3.set_forecast_type()
        self.assertIsNone(
            forecast_type,
            "set_forecast_type must return None when sale_line_id " "is in draft state",
        )

        # Condition 4: No stage and no sale line → "forecast" (else branch)
        project_no_stage = self.ProjectProject.create({"name": "NoStageNoSale"})
        project_no_stage.stage_id = False
        task_4 = self.ProjectTask.create(
            {
                "name": "NoStageNoSaleTask",
                "project_id": project_no_stage.id,
                "forecast_role_id": self.role_consultant.id,
            }
        )
        self.assertFalse(task_4.sale_line_id)
        forecast_type = task_4.set_forecast_type()
        self.assertEqual(
            forecast_type,
            "forecast",
            "set_forecast_type must return 'forecast' when neither "
            "stage_id nor sale_line_id is set",
        )
