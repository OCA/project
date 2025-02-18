# Copyright 2021 Pierre Verkest
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProject(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env.ref("project.project_project_1")
        cls.project.name = "Test project name"
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test plan"})
        cls.project.analytic_account_id = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic account name",
                "code": "Test Weird code",
                "plan_id": cls.plan.id,
            }
        )

    def test_search_project_by_account_analytic_code(self):
        result = self.env["project.project"].name_search(
            name=self.project.analytic_account_id.code
        )
        self.assertEqual(
            result[0][1],
            f"[{self.project.analytic_account_id.code}] {self.project.name}",
        )

    def test_project_display_name(self):
        self.assertEqual(
            self.project.display_name,
            f"[{self.project.analytic_account_id.code}] {self.project.name}",
        )
        self.project.analytic_account_id = False

        self.assertEqual(
            self.project.display_name,
            f"{self.project.name}",
        )
