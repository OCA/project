from unittest.mock import patch

from freezegun import freeze_time
from psycopg2 import IntegrityError

from odoo.tests.common import Form, TransactionCase, new_test_user, users
from odoo.tools import mute_logger


@freeze_time("2023-01-01 12:00:00")
class TestProjectSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        new_test_user(
            cls.env,
            "manager",
            "project.group_project_manager,analytic.group_analytic_accounting",
        )
        cls.pjr_seq = cls.env.ref("project_sequence.seq_project_sequence")
        cls.pjr_seq.date_range_ids.unlink()

        # Get the existing plan ID for the main company
        plan_model = cls.env["account.analytic.applicability"]
        main_company = cls.env.ref("base.main_company")
        existing_plans = plan_model.search([("company_id", "=", main_company.id)])
        if existing_plans:
            plan_id = existing_plans[0].id
        else:
            # No existing plan found for the main company, handle this case accordingly
            with patch.object(plan_model, "create") as create_mock:
                new_plan = create_mock.return_value
                new_plan.id = 1  # Set a mock ID for the new plan
                plan_id = new_plan.id

        # Create or update the analytic account for the main company
        analytic_account = cls.env["account.analytic.account"].search(
            [("name", "=", "aaa"), ("company_id", "=", main_company.id)], limit=1
        )
        if analytic_account:
            analytic_account.write({"plan_id": plan_id, "root_plan_id": plan_id})
        else:
            analytic_account = cls.env["account.analytic.account"].create(
                {
                    "name": "aaa",
                    "plan_id": plan_id,
                    "root_plan_id": plan_id,
                    "company_id": main_company.id,
                }
            )

        cls.analytic_account = analytic_account

    def setUp(self):
        super().setUp()
        self.pjr_seq._get_current_sequence().number_next = 11

    @users("manager")
    def test_sequence_after_creation(self):
        """Sequence is applied only after project creation."""
        prj_f = Form(self.env["project.project"])
        self.assertFalse(prj_f.name)
        self.assertFalse(prj_f.sequence_code)
        proj = prj_f.save()
        self.assertTrue(proj.sequence_code)
        self.assertEqual(proj.name, proj.sequence_code)
        self.assertEqual(proj.sequence_code, "23-00011")
        self.assertEqual(proj.display_name, "23-00011")

    def test_analytic_account_after_creation_no_name(self):
        """Project's analytic account is named like project's default name."""
        proj = self.env["project.project"].create(
            {"analytic_account_id": self.analytic_account.id}
        )
        self.assertEqual(proj.sequence_code, "23-00011")
        self.assertEqual(proj.name, "23-00011")
        self.assertEqual(proj.display_name, "23-00011")
        self.assertEqual(proj.analytic_account_id.name, "23-00011")

    def test_analytic_account_after_creation_named(self):
        """Project's analytic account is named like project's display name."""
        proj = self.env["project.project"].create(
            {"name": "whatever", "analytic_account_id": self.analytic_account.id}
        )
        self.assertEqual(proj.sequence_code, "23-00011")
        self.assertEqual(proj.name, "whatever")
        self.assertEqual(proj.display_name, "23-00011 - whatever")
        self.assertEqual(proj.analytic_account_id.name, "23-00011 - whatever")

    @users("manager")
    def test_sequence_copied_to_name_if_emptied(self):
        """Sequence is copied to project name if user removes it."""
        proj = self.env["project.project"].create(
            {"name": "whatever", "analytic_account_id": self.analytic_account.id}
        )
        self.assertEqual(proj.name, "whatever")
        self.assertEqual(proj.sequence_code, "23-00011")
        self.assertEqual(proj.display_name, "23-00011 - whatever")
        self.assertEqual(proj.analytic_account_id.name, "23-00011 - whatever")
        with Form(proj) as prj_f:
            prj_f.name = False
        self.assertEqual(proj.name, "23-00011")
        self.assertEqual(proj.sequence_code, "23-00011")
        self.assertEqual(proj.display_name, "23-00011")
        self.assertEqual(proj.analytic_account_id.name, "23-00011")

    @users("manager")
    def test_sequence_not_copied_to_another_project(self):
        """Sequence is not duplicated to another project."""
        proj1 = self.env["project.project"].create({"name": "whatever"})
        proj2 = proj1.copy()
        self.assertEqual(proj1.sequence_code, "23-00011")
        self.assertEqual(proj2.sequence_code, "23-00012")

    @users("manager")
    @mute_logger("odoo.sql_db")
    def test_sequence_unique(self):
        """Sequence cannot have duplicates."""
        proj1 = self.env["project.project"].create({"name": "one"})
        self.assertEqual(proj1.sequence_code, "23-00011")
        self.pjr_seq._get_current_sequence().number_next = 11
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            proj1 = self.env["project.project"].create({"name": "two"})

    @users("manager")
    def test_project_without_sequence(self):
        """Preexisting projects had no sequence, and they should display fine."""
        proj1 = self.env["project.project"].create(
            {"name": "one", "sequence_code": False}
        )
        self.assertEqual(proj1.display_name, "one")
        self.assertFalse(proj1.sequence_code)

        proj2 = self.env["project.project"].create({"name": "two"})
        self.assertEqual(proj2.sequence_code, "23-00011")
        self.assertEqual(proj2.display_name, "23-00011 - two")

        proj3 = self.env["project.project"].create(
            {"name": "three", "sequence_code": "23-00012"}
        )
        self.assertEqual(proj3.display_name, "23-00012 - three")
        self.assertEqual(proj3.sequence_code, "23-00012")

        # Creation of a new plan
        plan_model = self.env["project.plan"]
        new_plan = plan_model.create({"name": "New Plan"})
        self.assertEqual(new_plan.name, "New Plan")

        # Verification of plan_id assignment
        proj1.plan_id = new_plan.id
        self.assertEqual(proj1.plan_id, new_plan.id)

        # Checking plan_id and root_plan_id assignment
        count = self.env["project.project"].search_count([])
        count.write({"plan_id": new_plan.id, "root_plan_id": new_plan.id})
        updated_proj1 = self.env["project.project"].browse(proj1.id)
        self.assertEqual(updated_proj1.plan_id, new_plan.id)
        self.assertEqual(updated_proj1.root_plan_id, new_plan.id)
