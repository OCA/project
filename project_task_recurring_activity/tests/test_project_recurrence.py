from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestProjectrecurrence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env.user.groups_id += cls.env.ref("project.group_project_recurring_tasks")
        cls.recurring_activity = cls.env["recurring.activity"]
        cls.stage_a = cls.env["project.task.type"].create({"name": "a"})
        cls.stage_b = cls.env["project.task.type"].create({"name": "b"})

        cls.demo_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "demo",
                    "login": "demo_user",
                    "email": "dess@yourcompany.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [cls.env.ref("project.group_project_recurring_tasks").id],
                        )
                    ],
                }
            )
        )

        cls.demo_user2 = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "demo2",
                    "login": "demo_user2",
                    "email": "dess2@yourcompany.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [cls.env.ref("project.group_project_recurring_tasks").id],
                        )
                    ],
                }
            )
        )
        cls.mail_activity_a = cls.env["mail.activity.type"].create(
            {
                "name": "activity_a",
                "default_user_id": cls.demo_user.id,
                "summary": "summary",
            }
        )
        cls.mail_activity_b = cls.env["mail.activity.type"].create(
            {
                "name": "activity_b",
                "default_user_id": cls.demo_user.id,
            }
        )
        cls.project_recurring = (
            cls.env["project.project"]
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Recurring",
                    "type_ids": [
                        (4, cls.stage_a.id),
                        (4, cls.stage_b.id),
                    ],
                }
            )
        )

        cls.project_recurring2 = (
            cls.env["project.project"]
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Recurring",
                    "type_ids": [
                        (4, cls.stage_a.id),
                        (4, cls.stage_b.id),
                    ],
                }
            )
        )

        cls.project_recurring.message_subscribe(
            partner_ids=[cls.demo_user.partner_id.id]
        )
        cls.project_recurring2.message_subscribe(
            partner_ids=[cls.demo_user.partner_id.id]
        )

    def test_check_activity_fields(self):
        with freeze_time("2020-01-01"):
            form = Form(self.env["project.task"])
            form.name = "test recurring task"
            form.description = "my super recurring task"
            form.project_id = self.project_recurring
            form.date_deadline = datetime(2020, 2, 1)
            form.recurring_task = True
            form.repeat_interval = 1
            form.repeat_unit = "month"
            form.repeat_type = "forever"
            task = form.save()
        with self.assertRaisesRegex(
            UserError,
            "has no access to the document",
        ):
            self.recurring_activity.create(
                {
                    "project_task_id": task.id,
                    "activity_type_id": self.mail_activity_a.id,
                    "user_id": self.demo_user2.id,
                    "days_after_task_creation_date": 1,
                },
            )

    def test_recurrence_cron_repeat_forever(self):
        domain = [("project_id", "=", self.project_recurring.id)]
        with freeze_time("2020-01-01"):
            form = Form(self.env["project.task"])
            form.name = "test recurring task"
            form.description = "my super recurring task"
            form.project_id = self.project_recurring
            form.date_deadline = datetime(2020, 2, 1)

            form.recurring_task = True
            form.repeat_interval = 1
            form.repeat_unit = "month"
            form.repeat_type = "forever"
            task = form.save()
            task.allocated_hours = 2

            self.assertEqual(len(task.recurring_activity_ids), 0, "Must be equal to 0")
            self.assertEqual(len(task.activity_ids), 0, "Must be equal to 0")
            task.message_subscribe(partner_ids=[self.demo_user.partner_id.id])
            task.write(
                {
                    "recurring_activity_ids": [
                        (
                            0,
                            0,
                            {
                                "activity_type_id": self.mail_activity_a.id,
                                "days_after_task_creation_date": 0,
                                "user_id": self.demo_user.id,
                                "summary": "summary",
                                "description": "description",
                            },
                        )
                    ]
                }
            )
            self.assertEqual(len(task.activity_ids), 1, "Must be equal to 1")
            self.assertEqual(
                task.activity_ids.summary, "summary", "Must be equal to 'summary'"
            )
            self.assertTrue(
                task.recurrence_id, "Task should have recurrence configured"
            )
            self.assertEqual(task.recurrence_id.repeat_interval, 1)
            self.assertEqual(task.recurrence_id.repeat_unit, "month")
            self.assertEqual(
                self.env["project.task"].search_count(domain), 1, "Must be equal to 1"
            )
            self.env["project.task.recurrence"]._cron_create_recurring_tasks()
            self.assertEqual(
                self.env["project.task"].search_count(domain),
                1,
                "no extra task should be created",
            )

        with freeze_time("2020-01-15"):
            self.assertEqual(
                self.env["project.task"].search_count(domain), 1, "Must be equal to 1"
            )
            self.env["project.task.recurrence"]._cron_create_recurring_tasks()
            self.assertEqual(
                self.env["project.task"].search_count(domain), 1, "Must be equal to 1"
            )

        with freeze_time("2020-02-15"):
            self.env["project.task.recurrence"]._cron_create_recurring_tasks()
            self.assertEqual(
                self.env["project.task"].search_count(domain), 1, "Must be equal to 1"
            )

        with freeze_time("2020-02-16"):
            self.env["project.task.recurrence"]._cron_create_recurring_tasks()
            self.assertEqual(
                self.env["project.task"].search_count(domain), 1, "Must be equal to 1"
            )

        with freeze_time("2020-02-17"):
            self.env["project.task.recurrence"]._cron_create_recurring_tasks()
            self.assertEqual(
                self.env["project.task"].search_count(domain), 1, "Must be equal to 1"
            )

        with freeze_time("2020-03-15"):
            self.env["project.task.recurrence"]._cron_create_recurring_tasks()
            self.assertEqual(
                self.env["project.task"].search_count(domain), 2, "Must be equal to 2"
            )

        tasks = self.env["project.task"].search(domain)
        self.assertEqual(len(tasks), 2, "Must be equal to 2")
        self.assertEqual(len(tasks.mapped("activity_ids")), 2, "Must be equal to 2")
        self.assertEqual(
            len(tasks.mapped("recurring_activity_ids")), 2, "Must be equal to 2"
        )
        project_task = tasks[0]
        activity = self.recurring_activity.search(
            [("project_task_id", "=", project_task.id)]
        )
        self.assertEqual(activity.user_id, self.mail_activity_a.default_user_id)
        self.assertEqual(activity.summary, project_task.activity_summary)
        activity.write(
            {
                "description": "<p><br></p>",
                "summary": None,
                "activity_type_id": self.mail_activity_b.id,
            }
        )
        activity._compute_on_activity_type_id()
        self.assertEqual(activity.user_id, self.mail_activity_a.default_user_id)
        self.assertEqual(activity.description, self.mail_activity_b.default_note)
        self.assertEqual(activity.summary, self.mail_activity_b.summary)

    def test_create_recurring_tasks(self):
        """Check custom method dev"""
        domain = [("project_id", "=", self.project_recurring2.id)]
        with freeze_time("2020-01-01"):
            form = Form(self.env["project.task"])
            form.name = "test recurring task"
            form.description = "my super recurring task"
            form.project_id = self.project_recurring2
            form.date_deadline = datetime(2020, 2, 1)

            form.recurring_task = True
            form.repeat_interval = 1
            form.repeat_unit = "month"
            form.repeat_type = "forever"
            task = form.save()
            task.allocated_hours = 2

            task.message_subscribe(partner_ids=[self.demo_user.partner_id.id])
            task.write(
                {
                    "recurring_activity_ids": [
                        (
                            0,
                            0,
                            {
                                "activity_type_id": self.mail_activity_a.id,
                                "days_after_task_creation_date": 0,
                                "user_id": self.demo_user.id,
                                "summary": "summary",
                                "description": "description",
                            },
                        )
                    ]
                }
            )
        with freeze_time("2020-01-15"):
            self.assertEqual(
                self.env["project.task"].search_count(domain), 1, "Must be equal to 1"
            )
            task.recurrence_id.create_recurring_tasks()
            self.assertEqual(
                self.env["project.task"].search_count(domain), 2, "Must be equal to 2"
            )
            self.assertEqual(
                task.recurring_activity_ids[0]._get_next_date(),
                fields.Date.today() + timedelta(days=1),
                "Must be equal to `2020-01-16`",
            )
            self.env["recurring.activity"]._cron_create_activities()

        with freeze_time("2020-01-16"):
            activity = self.env["recurring.activity"].search(
                [("project_task_id", "=", task.id)]
            )
            self.assertEqual(
                len(activity),
                1,
                "Must be equal to 1",
            )
            self.assertEqual(
                activity.next_recurrence_date,
                fields.Date.today(),
                "Must be equal to `2020-01-16`",
            )
        with freeze_time("2020-02-15"):
            task.recurrence_id.create_recurring_tasks()
            self.assertEqual(
                self.env["project.task"].search_count(domain), 3, "Must be equal to 3"
            )
            today = fields.Date.today()
            self.assertEqual(
                self.env["recurring.activity"].delta_time(
                    today, today + timedelta(days=1)
                ),
                1,
                "Must be equal to 1",
            )

    def test_call_create_recurring_tasks(self):
        """Ensure button helper creates next recurring task."""
        domain = [("project_id", "=", self.project_recurring2.id)]
        with freeze_time("2020-01-01"):
            form = Form(self.env["project.task"])
            form.name = "test recurring task button"
            form.description = "my super recurring task"
            form.project_id = self.project_recurring2
            form.date_deadline = datetime(2020, 2, 1)

            form.recurring_task = True
            form.repeat_interval = 1
            form.repeat_unit = "month"
            form.repeat_type = "forever"
            task = form.save()
            task.allocated_hours = 2

            task.message_subscribe(partner_ids=[self.demo_user.partner_id.id])
            task.write(
                {
                    "recurring_activity_ids": [
                        (
                            0,
                            0,
                            {
                                "activity_type_id": self.mail_activity_a.id,
                                "days_after_task_creation_date": 0,
                                "user_id": self.demo_user.id,
                                "summary": "summary",
                                "description": "description",
                            },
                        )
                    ]
                }
            )

        with freeze_time("2020-01-15"):
            self.assertEqual(
                self.env["project.task"].search_count(domain),
                1,
                "There should be one recurring task before calling helper",
            )
            task.call_create_recurring_tasks()
            self.assertEqual(
                self.env["project.task"].search_count(domain),
                2,
                "Helper should create the next recurring task",
            )
