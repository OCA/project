# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestHrExpenseTask(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.other_project = cls.env["project.project"].create({"name": "Other Project"})
        cls.task = cls.env["project.task"].create(
            {"name": "Test Task", "project_id": cls.project.id}
        )
        cls.other_task = cls.env["project.task"].create(
            {"name": "Other Task", "project_id": cls.other_project.id}
        )
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee"})

    def test_task_id_can_be_set_for_its_own_project(self):
        expense = self.env["hr.expense"].create(
            {
                "name": "Test expense",
                "employee_id": self.employee.id,
                "project_id": self.project.id,
                "task_id": self.task.id,
                "total_amount_currency": 10.0,
            }
        )
        self.assertEqual(expense.task_id, self.task)

    def test_task_id_optional(self):
        expense = self.env["hr.expense"].create(
            {
                "name": "Test expense",
                "employee_id": self.employee.id,
                "project_id": self.project.id,
                "total_amount_currency": 10.0,
            }
        )
        self.assertFalse(expense.task_id)

    def test_task_from_another_project_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["hr.expense"].create(
                {
                    "name": "Test expense",
                    "employee_id": self.employee.id,
                    "project_id": self.project.id,
                    "task_id": self.other_task.id,
                    "total_amount_currency": 10.0,
                }
            )

    def test_task_distribution_is_propagated_to_expense(self):
        succursale_plan = self.env["account.analytic.plan"].create(
            {"name": "Succursales"}
        )
        metiers_plan = self.env["account.analytic.plan"].create({"name": "Metiers"})
        succursale_account = self.env["account.analytic.account"].create(
            {"name": "Succursale A", "plan_id": succursale_plan.id}
        )
        metiers_account = self.env["account.analytic.account"].create(
            {"name": "Metier B", "plan_id": metiers_plan.id}
        )

        # Dynamic analytic plan fields are created from plan column names.
        self.task[succursale_plan._column_name()] = succursale_account
        self.task[metiers_plan._column_name()] = metiers_account

        expense = self.env["hr.expense"].create(
            {
                "name": "Expense with task plans",
                "employee_id": self.employee.id,
                "project_id": self.project.id,
                "task_id": self.task.id,
                "total_amount_currency": 10.0,
            }
        )

        self.assertEqual(
            expense.analytic_distribution,
            self.task._get_analytic_distribution(),
            "The expense analytic distribution should follow the selected task plans.",
        )
