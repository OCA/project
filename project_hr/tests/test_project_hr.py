# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestProjectHr(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_model = cls.env["res.users"]
        cls.user = cls.user_model.create(
            {"login": "test_project_hr", "name": "Test user"}
        )
        cls.user_2 = cls.user_model.create(
            {"login": "test_project_hr_2", "name": "Test user 2"}
        )
        cls.hr_category = cls.env["hr.employee.category"].create(
            {"name": "Test employee category"}
        )
        cls.hr_category_2 = cls.env["hr.employee.category"].create(
            {"name": "Test employee category 2"}
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test employee",
                "user_id": cls.user.id,
                "category_ids": [(6, 0, cls.hr_category.ids)],
            }
        )
        cls.project = cls.env["project.project"].create(
            {"name": "Test project", "hr_category_ids": [(4, cls.hr_category.id)]}
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test task",
                "project_id": cls.project.id,
                "hr_category_ids": [(4, cls.hr_category.id)],
                "user_id": cls.user.id,
            }
        )

    def test_user(self):
        self.assertEqual(self.user.hr_category_ids, self.hr_category)
        self.employee.category_ids = [(4, self.hr_category_2.id)]
        self.assertEqual(
            self.user.hr_category_ids, self.hr_category + self.hr_category_2
        )
        self.hr_category_3 = self.env["hr.employee.category"].create(
            {"name": "Test employee category 3"}
        )
        # Check if need invalidate cache
        self.employee.category_ids = [(4, self.hr_category_3.id)]
        self.assertEqual(
            self.user.hr_category_ids,
            self.hr_category + self.hr_category_2 + self.hr_category_3,
        )

    def test_task(self):
        self.assertEqual(self.task.employee_id, self.employee)
        self.assertEqual(self.task.allowed_hr_category_ids, self.hr_category)
        self.project.hr_category_ids = [(4, self.hr_category_2.id)]
        self.assertEqual(
            self.task.allowed_hr_category_ids, self.hr_category + self.hr_category_2
        )
        self.assertEqual(self.task.allowed_user_ids, self.user)
        self.env["hr.employee"].create(
            {
                "name": "Test employee 2",
                "user_id": self.user_2.id,
                "category_ids": [(6, 0, self.hr_category.ids)],
            }
        )
        self.assertEqual(self.task.allowed_user_ids, self.user + self.user_2)
        # Test _check_employee_category_user constraint
        with self.assertRaises(ValidationError):
            self.task.hr_category_ids = [(4, self.hr_category_2.id)]
        with self.assertRaises(ValidationError):
            self.task.user_id = self.user_2.id
        # Test _check_employee_category_project constraint
        self.project.hr_category_ids = [(4, self.hr_category_2.id)]
        with self.assertRaises(ValidationError):
            self.task.hr_category_ids = [(4, self.hr_category_2.id)]

    def test_task_project_wo_categories(self):
        self.project.hr_category_ids = False
        self.assertTrue(self.task.allowed_hr_category_ids)
        # This operation shouldn't give error
        self.task.hr_category_ids = [(4, self.hr_category.id)]
