from freezegun import freeze_time

from odoo.tests import TransactionCase


class TestProjectSprint(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.project = cls.env["project.project"].create(
            {"name": "Test Project", "user_id": cls.user_demo.id}
        )
        cls.sprint = cls.env["project.sprint"].create(
            {
                "name": "Test Sprint",
                "user_ids": [(4, cls.user_demo.id)],
                "project_id": cls.project.id,
                "date_start": "2024-08-28",
                "date_end": "2024-09-15",
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
                "user_ids": [(4, cls.user_demo.id)],
                "sprint_id": cls.sprint.id,
            }
        )

    def test_state_project_sprint(self):
        self.assertEqual(self.sprint.state, "draft")
        self.sprint.action_start()
        self.assertEqual(self.sprint.state, "in_progress")
        self.sprint.action_done()
        self.assertEqual(self.sprint.state, "done")

    @freeze_time("2024-08-30")
    def test_check_project_update(self):
        self.sprint_2 = self.env["project.sprint"].create(
            {
                "name": "Test Sprint 2",
                "user_ids": [(4, self.user_demo.id)],
                "project_id": self.project.id,
                "date_start": "2024-08-10",
                "date_end": "2024-08-28",
                "state": "in_progress",
            }
        )
        self.sprint.state = "draft"
        self.sprint.cron_update_sprint_state()
        self.assertEqual(self.sprint.state, "in_progress")
        self.assertEqual(self.sprint_2.state, "done")

    def test_task_count(self):
        self.assertEqual(self.sprint.tasks_count, 1)
        self.task.sprint_id = False
        self.sprint._compute_tasks_count()
        self.assertEqual(self.sprint.tasks_count, 0)

    def test_compute_end_date(self):
        self.assertEqual(self.sprint.date_end.strftime("%Y-%m-%d"), "2024-09-15")
        self.sprint.date_option = "1_months"
        self.sprint._compute_date_end()
        self.assertEqual(self.sprint.date_end.strftime("%Y-%m-%d"), "2024-09-28")
        self.sprint.date_option = "custom"
        self.sprint._compute_date_end()
        self.assertEqual(self.sprint.date_end.strftime("%Y-%m-%d"), "2024-08-29")

    def test_action_task(self):
        action = self.sprint.action_tasks()
        self.assertEqual(action["res_model"], "project.task")
        self.assertEqual(action["domain"], [("sprint_id", "=", self.sprint.id)])
        self.assertEqual(
            action["context"],
            {
                "default_project_id": self.project.id,
                "default_sprint_id": self.sprint.id,
            },
        )
