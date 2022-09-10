# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import SavepointCase


class TestTasckSchedule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project = cls.env.ref(
            "project_task_recurring.project_project_with_recurrence"
        )
        cls.schedule_obj = cls.env["project.task.schedule"]

    def test_task_schedule(self):
        """
            Set project schedules with next recurrency date as yesterday
            Execute the cron
            One task should have been created (one schedule is draft)
        """
        tasks_before = self.project.task_ids
        next_date = fields.Datetime.now() + relativedelta(days=-1)
        for schedule in self.project.task_schedule_ids:
            schedule.next_recurrency_date = next_date
            schedule.last_recurrency_date = next_date
        self.schedule_obj._schedule_cron()
        tasks_after = self.project.task_ids - tasks_before
        self.assertEqual(1, len(tasks_after))
        for schedule in self.project.task_schedule_ids.filtered_domain(
            self.project.task_schedule_ids._get_schedule_domain()
        ):
            new_next_date = next_date + schedule.get_relative_delta(
                schedule.recurrence_type
            )
            self.assertEqual(schedule.next_recurrency_date, new_next_date)

    def test_task_activation(self):
        """
            Set project schedules with next recurrency date as yesterday
            Execute the cron
            One task should have been created (one schedule is draft)
        """
        tasks_before = self.project.task_ids
        next_date = fields.Datetime.now() + relativedelta(days=-1)
        # Inactivate schedules

        for schedule in self.project.task_schedule_ids:
            schedule.next_recurrency_date = next_date
            schedule.last_recurrency_date = next_date
        self.project.task_schedule_ids.inactive()
        self.schedule_obj._schedule_cron()
        tasks_after = self.project.task_ids - tasks_before
        self.assertEqual(0, len(tasks_after))

        # Set them draft
        self.project.task_schedule_ids.draft()
        self.assertEqual(
            ["draft", "draft"], self.project.task_schedule_ids.mapped("state")
        )

        # Activate schedules
        self.project.task_schedule_ids.active()
        for schedule in self.project.task_schedule_ids:
            schedule.next_recurrency_date = next_date
            schedule.last_recurrency_date = next_date

        self.schedule_obj._schedule_cron()
        tasks_after = self.project.task_ids - tasks_before
        # As the initial draft schedule was draft, it is now activated
        self.assertEqual(2, len(tasks_after))
        for task in tasks_after:
            activity = task.activity_ids.filtered(
                lambda a: "New Recurring Task" in a.display_name
            )
            self.assertTrue(activity)
