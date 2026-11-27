# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo.addons.base.tests.common import BaseCommon


class TestProjectProjectAnalyticAccountName(BaseCommon):
    # The test does not check permissions: keep running as the superuser.
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create({"name": "Original Name"})
        cls.project._create_analytic_account()
        cls.analytic_account = cls.project.account_id
        cls.original_analytic_name = cls.analytic_account.name

    def test_analytic_account_name_preserved_on_project_rename(self):
        """Renaming a project keeps its analytic account name unchanged."""
        self.assertTrue(self.analytic_account)
        self.assertEqual(self.analytic_account.name, "Original Name")
        self.project.write({"name": "New Name"})
        self.assertEqual(self.project.name, "New Name")
        self.assertEqual(
            self.analytic_account.name,
            self.original_analytic_name,
            "The analytic account name should not change when the project is renamed.",
        )
