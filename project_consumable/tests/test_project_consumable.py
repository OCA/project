# Copyright 2021-2025 - Pierre Verkest
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import TransactionCase, new_test_user, users


class TestProjectConsumable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("project_consumable.product_coffee_capsule")
        default_plan_id = cls.env["account.analytic.plan"].search([], limit=1)
        cls.customer = cls.env["res.partner"].create({"name": "a customer"})
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
                "allow_consumables": True,
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.employee = cls.user_demo.employee_id
        cls.project_user = new_test_user(
            cls.env,
            login="test.project.user",
            groups="project.group_project_user,hr_timesheet.group_hr_timesheet_user",
        )
        cls.project_manager = new_test_user(
            cls.env,
            login="test.project.manager",
            groups="project.group_project_manager,hr_timesheet.group_timesheet_manager",
        )

    def test_onchange_product_type_project_ok_to_be_true(self):
        self.product.project_ok = False
        self.product.type = "consu"
        self.assertTrue(self.product.project_ok)

    def test_onchange_product_type_project_ok_to_be_false(self):
        self.product.project_ok = True
        self.product.type = "service"
        self.assertFalse(self.product.project_ok)

    def _prepare_consumable_line_data(self, **kwargs):
        data = {
            "name": "collect test material",
            "consumable_project_id": self.project.id,
            "account_id": None,
            "product_id": self.product.id,
            "unit_amount": 6,
            "product_uom_id": self.product.uom_id.id,
            "task_id": None,
            "amount": None,
            "date": None,
            "partner_id": None,
        }
        data.update(**kwargs)
        return {k: v for k, v in data.items() if v is not None}

    @users("test.project.user")
    def test_user_create(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data()
        )
        self.assertEqual(account_analytic_line.user_id.id, self.project_user.id)

    @users("test.project.user")
    def test_user_create_for_someone_else_failed(self):
        with self.assertRaises(AccessError):
            self.env["account.analytic.line"].create(
                self._prepare_consumable_line_data(user_id=self.project_manager.id)
            )

    @users("test.project.manager")
    def test_manager_create(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(user_id=self.project_user.id)
        )
        self.assertEqual(account_analytic_line.user_id.id, self.project_user.id)

    @users("demo")
    def test_user_id(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(user_id=None)
        )
        self.assertEqual(account_analytic_line.user_id.id, self.env.user.id)

    def test_name(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(name=None)
        )
        self.assertEqual(account_analytic_line.name, "/")

    def test_date(self):
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(date=None)
        )
        self.assertEqual(account_analytic_line.date, date.today())

    def test_partner_id_from_account(self):
        self.analytic_account.partner_id = self.customer
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data()
        )
        self.assertEqual(account_analytic_line.partner_id, self.customer)

    def test_partner_id_from_project(self):
        self.project.partner_id = self.customer
        account_analytic_line = self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data()
        )
        self.assertEqual(account_analytic_line.partner_id, self.customer)

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
        # self.product.standard_price = 0.33
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

    @users("demo")
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

    def test_project_with_inactive_analytic_account_raise(self):
        self.project.analytic_account_id.active = False
        with self.assertRaisesRegex(
            ValidationError,
            r"Materials must be created on a project with "
            r"an active analytic account",
        ):
            self.env["account.analytic.line"].create(
                self._prepare_consumable_line_data(
                    unit_amount=7,
                    product_uom_id=self.env.ref(
                        "project_consumable.uom_cat_coffee_capsule_box_10"
                    ).id,
                )
            )

    def test_project_without_analytic_account_raise(self):
        with self.assertRaisesRegex(
            ValidationError, r"You cannot use consumables without an analytic account"
        ):
            self.project.analytic_account_id = False

    def test_action_project_consumable(self):
        action = self.project.action_project_consumable()
        self.assertEqual(
            action["domain"], [("consumable_project_id", "in", self.project.ids)]
        )

    def test_get_stat_buttons(self):
        buttons = self.project._get_stat_buttons()
        self.assertTrue(
            "action_project_consumable" in [button["action"] for button in buttons],
            buttons,
        )

    def test_get_stat_buttons_non_project_manager(self):
        user_demo = self.env.ref("base.user_demo")
        self.assertFalse(user_demo.has_group("project.group_project_manager"))
        buttons = self.project.with_user(user_demo)._get_stat_buttons()
        self.assertTrue(
            "action_project_consumable" not in [button["action"] for button in buttons],
            buttons,
        )
