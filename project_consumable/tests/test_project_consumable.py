# Copyright 2021 - Pierre Verkest
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date

from odoo.tests import TransactionCase, users


class TestProjectConsumable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("project_consumable.product_coffee_capsule")
        default_plan_id = cls.env["account.analytic.plan"].search([], limit=1)
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test",
                "plan_id": default_plan_id.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test",
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.employee = cls.user_demo.employee_id

    def test_onchange_product_type_project_ok_to_be_true(self):
        self.product.project_ok = False
        self.product.type = "consu"
        self.product.product_tmpl_id._onchange_type()
        self.assertTrue(self.product.project_ok)

    def test_onchange_product_type_project_ok_to_be_false(self):
        self.product.project_ok = True
        self.product.type = "service"
        self.product.product_tmpl_id._onchange_type()
        self.assertFalse(self.product.project_ok)

    def _prepare_consumable_line_data(self, **kwargs):
        data = {
            "name": "collect test material",
            "project_id": self.project.id,
            "account_id": None,
            "product_id": self.product.id,
            "unit_amount": 6,
            "employee_id": self.employee.id,
            "product_uom_id": self.product.uom_id.id,
            "task_id": None,
            "amount": None,
            "date": None,
            "partner_id": None,
        }
        data.update(**kwargs)
        return {k: v for k, v in data.items() if v is not None}

    @users("demo")
    def test_no_employee(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(employee_id=None)
        )
        self.assertEqual(account_analytic_line.employee_id, self.employee)

    def test_user_id(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(user_id=None)
        )
        self.assertEqual(account_analytic_line.user_id.id, self.user_demo.id)

    def test_date(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(date=None)
        )
        self.assertEqual(account_analytic_line.date, date.today())

    def test_analytic_account_set_from_project(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(account_id=None)
        )
        self.assertEqual(
            account_analytic_line.account_id.id, self.project.analytic_account_id.id
        )

    def test_consumable_amount_force_uom(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(
                unit_amount=7,
                product_uom_id=self.env.ref(
                    "project_consumable.uom_cat_coffee_capsule_box_10"
                ).id,
            )
        )
        self.assertEqual(
            account_analytic_line.amount,
            # -1: cost are negative
            # 7: product quantity
            # 10: coffee box
            # 0.33 product unit cost
            -1 * 7 * 10 * 0.33,
        )

    def test_consumable_amount_default_product_uom(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(unit_amount=6, product_uom_id=None)
        )
        self.assertEqual(
            account_analytic_line.amount,
            # -1: cost are negative
            # 7: product quantity
            # 0.33 product unit cost
            -1 * 6 * 0.33,
        )
        self.assertEqual(
            account_analytic_line.product_uom_id.id,
            self.env.ref("project_consumable.uom_cat_coffee_capsule_unit").id,
        )

    def test_timesheet(self):
        """Ensure we don't break timesheets behaviors"""
        account_analytic_line = self.env["account.analytic.line"].create(
            {
                "name": "test timesheet",
                "project_id": self.project.id,
                "unit_amount": 3,
                "employee_id": self.employee.id,
            }
        )
        self.assertEqual(
            account_analytic_line.account_id.id, self.project.analytic_account_id.id
        )
        self.assertEqual(
            account_analytic_line.product_uom_id.id,
            self.env.ref("uom.product_uom_hour").id,
        )
        timesheet_cost = 75
        self.assertEqual(account_analytic_line.amount, -timesheet_cost * 3)

    def test_consumable_count(self):
        self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(
                unit_amount=7,
                product_uom_id=self.env.ref(
                    "project_consumable.uom_cat_coffee_capsule_box_10"
                ).id,
            )
        )
        self.assertEqual(self.project.consumable_count, 1)
