# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.exceptions import ValidationError
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon

_logger = logging.getLogger(__name__)


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
                "category_ids": [(6, 0, cls.hr_category.ids)],
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test project",
                "hr_category_ids": [(4, cls.hr_category.id)],
                "company_id": cls.env.company.id,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test task",
                "project_id": cls.project.id,
                "hr_category_ids": [(4, cls.hr_category.id)],
                "user_ids": [(6, 0, [cls.user1.id])],
            }
        )

    def test_user(self):
        self.assertEqual(self.user1.hr_category_ids, self.hr_category)
        self.employee.category_ids = [(4, self.hr_category_2.id)]
        self.assertEqual(
            self.user1.hr_category_ids, self.hr_category + self.hr_category_2
        )
        # Check if need invalidate cache
        self.employee.category_ids = [(4, self.hr_category_3.id)]
        self.assertEqual(
            self.user1.hr_category_ids,
            self.hr_category + self.hr_category_2 + self.hr_category_3,
        )

    def test_task(self):
        # check computed values on task
        self.assertEqual(self.task.employee_ids, self.employee)
        self.assertEqual(self.task.allowed_hr_category_ids, self.hr_category)
        self.assertEqual(self.task.allowed_assigned_user_ids, self.user1)
        self.project.hr_category_ids = [(4, self.hr_category_2.id)]
        self.assertEqual(
            self.task.allowed_hr_category_ids, self.hr_category + self.hr_category_2
        )
        self.env["hr.employee"].create(
            {
                "name": "Test employee 2",
                "user_id": self.user2.id,
                "category_ids": [(6, 0, self.hr_category.ids)],
            }
        )
        self.assertEqual(self.task.allowed_assigned_user_ids, self.user1 + self.user2)
        # Test _check_employee_category_user constraint
        with self.assertRaises(ValidationError):
            self.task.hr_category_ids = [(4, self.hr_category_2.id)]
        # Test _check_employee_category_project constraint
        self.project.hr_category_ids = [(4, self.hr_category_2.id)]
        with self.assertRaises(ValidationError):
            self.task.hr_category_ids = [(4, self.hr_category_2.id)]
        # add employee to category hr_category_3
        self.employee.category_ids = [(4, self.hr_category_3.id)]
        # test assign a category no in project categories
        with self.assertRaises(ValidationError):
            self.task.hr_category_ids = [(4, self.hr_category_3.id)]

    def test_task_project_wo_categories(self):
        self.project.hr_category_ids = False
        self.assertTrue(self.task.allowed_hr_category_ids)
        # This operation shouldn't give error
        self.task.hr_category_ids = [(4, self.hr_category.id)]
