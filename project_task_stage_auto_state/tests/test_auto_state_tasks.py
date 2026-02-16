# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


@freeze_time("2026-01-01")
class TestAutoStateDoneCancel(TransactionCase):
    """Tests for auto-done / auto-cancel functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.date_trigger, cls.date_not_trigger = "2025-12-25", "2025-12-29"
        cls.stage_auto_done = cls.env["project.task.type"].create(
            {
                "name": "Auto Done In Progress",
                "auto_done_days": 5,
                "allow_done_from_in_progress": True,
                "project_ids": [(4, cls.project.id)],
            }
        )
        cls.stage_auto_cancel = cls.env["project.task.type"].create(
            {
                "name": "Auto Cancel In Progress",
                "auto_cancel_days": 5,
                "allow_cancel_from_in_progress": True,
                "project_ids": [(4, cls.project.id)],
            }
        )
        cls.stage_not_auto = cls.env["project.task.type"].create(
            {
                "name": "No Auto",
                "project_ids": [(4, cls.project.id)],
            }
        )

    def test_auto_done_trigger_days(self):
        """Task is auto-marked as done after configured days."""
        task = self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": self.project.id,
                "stage_id": self.stage_auto_done.id,
            }
        )
        self.assertEqual(task.state, "01_in_progress")
        task.date_last_stage_update = self.date_trigger
        self.env["project.task"].auto_change_task_state_by_stage()
        self.assertEqual(task.state, "1_done")

    def test_auto_cancel_trigger_days(self):
        """Task is auto-marked as cancelled after configured days."""
        task = self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": self.project.id,
                "stage_id": self.stage_auto_cancel.id,
            }
        )
        self.assertEqual(task.state, "01_in_progress")
        task.date_last_stage_update = self.date_trigger
        self.env["project.task"].auto_change_task_state_by_stage()
        self.assertEqual(task.state, "1_canceled")

    def test_not_auto_done_not_trigger_days(self):
        """Task is NOT auto-marked before configured days."""
        task = self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": self.project.id,
                "stage_id": self.stage_auto_done.id,
            }
        )
        self.assertEqual(task.state, "01_in_progress")
        task.date_last_stage_update = self.date_not_trigger
        self.env["project.task"].auto_change_task_state_by_stage()
        self.assertEqual(task.state, "01_in_progress")

    def test_not_auto_done_not_allowed_state(self):
        """Task in allowed state is auto-marked."""
        task = self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": self.project.id,
                "stage_id": self.stage_auto_done.id,
                "state": "03_approved",
            }
        )
        self.assertEqual(task.state, "03_approved")
        task.date_last_stage_update = self.date_trigger
        self.env["project.task"].auto_change_task_state_by_stage()
        self.assertEqual(task.state, "03_approved")

    def test_not_auto_done_on_disabled_stage(self):
        """Stage with auto_done_days=0 does nothing."""
        task = self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": self.project.id,
                "stage_id": self.stage_not_auto.id,
            }
        )
        self.assertEqual(task.state, "01_in_progress")
        task.date_last_stage_update = self.date_trigger
        self.env["project.task"].auto_change_task_state_by_stage()
        self.assertEqual(task.state, "01_in_progress")

    def test_not_auto_done_on_closed_states(self):
        """Already closed tasks (done/canceled) are ignored."""
        for state in ("1_done", "1_canceled"):
            task = self.env["project.task"].create(
                {
                    "name": "Task",
                    "project_id": self.project.id,
                    "stage_id": self.stage_auto_done.id,
                    "state": state,
                }
            )
            messages_before = len(task.message_ids)
            task.date_last_stage_update = self.date_trigger
            self.env["project.task"].auto_change_task_state_by_stage()
            self.assertEqual(task.state, state)
            self.assertEqual(len(task.message_ids), messages_before)

    def test_auto_done_posts_message(self):
        """Chatter message is posted when task is auto-marked done."""
        task = self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": self.project.id,
                "stage_id": self.stage_auto_done.id,
            }
        )
        task.date_last_stage_update = self.date_trigger
        previous_messages = task.message_ids
        self.env["project.task"].auto_change_task_state_by_stage()
        self.assertGreater(len(task.message_ids), len(previous_messages))
        self.assertTrue(
            any(
                [
                    "task automatically" in message.body.lower()
                    for message in task.message_ids
                ]
            )
        )

    def test_constraint_auto_done(self):
        """auto_done_days > 0 requires at least one allowed state."""
        with self.assertRaises(ValidationError):
            self.env["project.task.type"].create(
                {
                    "name": "Invalid Task Type",
                    "auto_done_days": 5,
                }
            )

    def test_constraint_auto_cancel(self):
        """auto_cancel_days > 0 requires at least one allowed state."""
        with self.assertRaises(ValidationError):
            self.env["project.task.type"].create(
                {
                    "name": "Invalid Task Type",
                    "auto_cancel_days": 5,
                }
            )
