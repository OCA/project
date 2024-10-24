from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestProjectTask(TransactionCase):
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
                "date_start": "2021-01-01",
                "date_end": "2021-01-15",
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

    def test_check_user_ids(self):
        with self.assertRaises(ValidationError):
            self.task.user_ids = [(4, self.user_admin.id)]

    def test_onchange_sprint_id(self):
        self.task._onchange_sprint_id()
        self.assertEqual(len(self.task.user_ids), 0)
