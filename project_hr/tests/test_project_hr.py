# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestProjectHr(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env.company
        cls.company_b = cls.env["res.company"].create({"name": "Test company B"})
        # Test users to use through the various tests
        cls.user1 = new_test_user(
            cls.env,
            login="test-user1",
            groups="project.group_project_user",
            company_id=cls.company_a.id,
            company_ids=[Command.set((cls.company_a + cls.company_b).ids)],
        )
        cls.user2 = new_test_user(
            cls.env,
            login="test-user2",
            groups="project.group_project_user",
            company_id=cls.company_a.id,
            company_ids=[Command.set((cls.company_a + cls.company_b).ids)],
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
                "company_id": cls.company_a.id,
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

    def test_user_multi_company(self):
        # User with company A + allowed_company_ids=A: hr_category
        user1_company_a = self.user1.with_company(self.company_a).with_context(
            allowed_company_ids=self.company_a.ids
        )
        user1_company_a.invalidate_recordset(["employee_ids"])
        self.assertIn(self.hr_category, user1_company_a.hr_category_ids)
        self.assertNotIn(self.hr_category_3, user1_company_a.hr_category_ids)
        self.assertNotIn(self.hr_category_3, user1_company_a.hr_category_ids)
        # User with company B + allowed_company_ids=B: False
        user1_company_b = self.user1.with_company(self.company_b).with_context(
            allowed_company_ids=self.company_b.ids
        )
        user1_company_b.invalidate_recordset(["employee_ids"])
        self.assertFalse(user1_company_b.hr_category_ids)
        # create employee company b with hr_category_2
        self.env["hr.employee"].create(
            {
                "name": "Test employee",
                "company_id": self.company_b.id,
                "user_id": self.user1.id,
                "category_ids": [(6, 0, self.hr_category_2.ids)],
            }
        )
        # User with company B + allowed_company_ids=B: hr_category_2
        user1_company_b = self.user1.with_company(self.company_b).with_context(
            allowed_company_ids=self.company_b.ids
        )
        user1_company_b.invalidate_recordset(["employee_ids"])
        self.assertNotIn(self.hr_category, user1_company_b.hr_category_ids)
        self.assertIn(self.hr_category_2, user1_company_b.hr_category_ids)
        self.assertNotIn(self.hr_category_3, user1_company_b.hr_category_ids)
        # User with company A + allowed_company_ids=A+B: hr_category
        user1_company_b = self.user1.with_company(self.company_a).with_context(
            allowed_company_ids=(self.company_a + self.company_b).ids
        )
        user1_company_b.invalidate_recordset(["employee_ids"])
        self.assertIn(self.hr_category, user1_company_b.hr_category_ids)
        self.assertNotIn(self.hr_category_2, user1_company_b.hr_category_ids)
        self.assertNotIn(self.hr_category_3, user1_company_b.hr_category_ids)

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
                "company_id": self.company_a.id,
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
