# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestProjectHr(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Test users to use through the various tests
        cls.user1 = new_test_user(
            cls.env,
            login="test-user1",
            groups="base.group_user,project.group_project_user",
        )
        cls.user2 = new_test_user(
            cls.env,
            login="test-user2",
            groups="base.group_user,project.group_project_user",
        )
        cls.hr_category = cls.env["hr.employee.category"].create(
            {"name": "Test employee category"}
        )
        cls.hr_category_2 = cls.env["hr.employee.category"].create(
            {"name": "Test employee category 2"}
        )

        cls.hr_category_3 = cls.env["hr.employee.category"].create(
            {"name": "Test employee category 3"}
        )

        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test employee",
                "user_id": cls.user1.id,
                "category_ids": [Command.set(cls.hr_category.ids)],
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test project",
                "hr_category_ids": [Command.link(cls.hr_category.id)],
                "company_id": cls.env.company.id,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test task",
                "project_id": cls.project.id,
                "hr_category_ids": [Command.link(cls.hr_category.id)],
                "user_ids": [Command.set(cls.user1.ids)],
            }
        )

    def test_user(self):
        self.assertEqual(self.user1.hr_category_ids, self.hr_category)
        self.employee.category_ids = [Command.link(self.hr_category_2.id)]
        self.assertEqual(
            self.user1.hr_category_ids, self.hr_category + self.hr_category_2
        )
        # Check if need invalidate cache
        self.employee.category_ids = [Command.link(self.hr_category_3.id)]
        self.assertEqual(
            self.user1.hr_category_ids,
            self.hr_category + self.hr_category_2 + self.hr_category_3,
        )

    def test_task(self):
        # check computed values on task
        category_model = self.env["hr.employee.category"]
        user_model = self.env["res.users"]
        self.assertEqual(self.task.employee_ids, self.employee)
        task_categories = category_model.search(self.task.domain_hr_category_ids)
        self.assertIn(self.hr_category, task_categories)
        self.assertNotIn(self.hr_category_2, task_categories)
        task_users = user_model.search(self.task.domain_user_ids)
        self.assertIn(self.user1, task_users)
        self.assertNotIn(self.user2, task_users)
        self.project.hr_category_ids = [Command.link(self.hr_category_2.id)]
        task_categories = category_model.search(self.task.domain_hr_category_ids)
        self.assertIn(self.hr_category, task_categories)
        self.assertIn(self.hr_category_2, task_categories)
        self.env["hr.employee"].create(
            {
                "name": "Test employee 2",
                "user_id": self.user2.id,
                "category_ids": [Command.set(self.hr_category.ids)],
            }
        )
        task_users = user_model.search(self.task.domain_user_ids)
        self.assertIn(self.user1, task_users)
        self.assertIn(self.user2, task_users)
        # Test _check_employee_category_user constraint
        with self.assertRaises(ValidationError):
            self.task.hr_category_ids = [Command.link(self.hr_category_2.id)]
        # Test _check_employee_category_project constraint
        self.project.hr_category_ids = [Command.link(self.hr_category_2.id)]
        with self.assertRaises(ValidationError):
            self.task.hr_category_ids = [Command.link(self.hr_category_2.id)]
        # add employee to category hr_category_3
        self.employee.category_ids = [Command.link(self.hr_category_3.id)]
        # test assign a category no in project categories
        with self.assertRaises(ValidationError):
            self.task.hr_category_ids = [Command.link(self.hr_category_3.id)]

    def test_task_project_wo_categories(self):
        self.project.hr_category_ids = False
        task_categories = self.env["hr.employee.category"].search(
            self.task.domain_hr_category_ids
        )
        self.assertIn(self.hr_category, task_categories)
        self.assertIn(self.hr_category_2, task_categories)
        # This operation shouldn't give error
        self.task.hr_category_ids = [Command.link(self.hr_category.id)]
