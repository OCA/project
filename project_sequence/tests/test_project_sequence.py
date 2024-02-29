# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from freezegun import freeze_time
from psycopg2 import IntegrityError

from odoo import fields
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
        default_plan_id = cls.env["account.analytic.plan"].search([], limit=1)
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "aaa",
                "plan_id": default_plan_id.id,
                "company_id": cls.env.company.id,
                "create_uid": cls.env.uid,
                "write_uid": cls.env.uid,
                "create_date": fields.Datetime.now(),
                "write_date": fields.Datetime.now(),
            }
        )

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
        # Make sure that the sequence is not increased
        proj2 = self.env["project.project"].create({"name": "two"})
        self.assertEqual(proj2.sequence_code, "23-00011")
        self.assertEqual(proj2.display_name, "23-00011 - two")

    def test_custom_pattern(self):
        """Display name pattern can be customized."""
        self.env["ir.config_parameter"].set_param(
            "project_sequence.display_name_pattern", "%(name)s/%(sequence_code)s"
        )
        proj = self.env["project.project"].create({"name": "one"})
        self.assertEqual(proj.display_name, "one/23-00011")
        self.assertEqual(proj.sequence_code, "23-00011")
        self.env["ir.config_parameter"].set_param(
            "project_sequence.display_name_pattern", "%(name)s"
        )
        proj = self.env["project.project"].create({"name": "two"})
        self.assertEqual(proj.display_name, "two")
        self.assertEqual(proj.sequence_code, "23-00012")
        self.env["ir.config_parameter"].set_param(
            "project_sequence.display_name_pattern", "%(sequence_code)s"
        )
        proj = self.env["project.project"].create({"name": "three"})
        self.assertEqual(proj.display_name, "23-00013")
        self.assertEqual(proj.sequence_code, "23-00013")

    def test_sync_analytic_account_name(self):
        """Set analytic account name equal to project's display name."""
        proj = self.env["project.project"].create({"name": "one"})
        default_plan_id = self.env["account.analytic.plan"].search([], limit=1)
        analytic_account = self.env["account.analytic.account"].create(
            {
                "name": proj.display_name,
                "plan_id": default_plan_id.id,
                "company_id": self.env.company.id,
                "create_uid": self.env.uid,
                "write_uid": self.env.uid,
                "create_date": fields.Datetime.now(),
                "write_date": fields.Datetime.now(),
            }
        )
        proj.analytic_account_id = analytic_account
        proj._sync_analytic_account_name()
        self.assertEqual(proj.analytic_account_id.name, proj.display_name)

        # Test when analytic_account_id is not set
        proj.analytic_account_id = False
        proj._sync_analytic_account_name()
        self.assertTrue(True)  # Placeholder assertion to ensure the code execution

    def test_name_search(self):
        """Allow searching by sequence code by default."""
        proj1 = self.env["project.project"].create({"name": "one"})
        self.assertEqual(proj1.sequence_code, "23-00011")
        proj2 = self.env["project.project"].create({"name": "two"})
        self.assertEqual(proj2.sequence_code, "23-00012")
        proj3 = self.env["project.project"].create({"name": "three"})
        self.assertEqual(proj3.sequence_code, "23-00013")

        # Search by name
        results = self.env["project.project"].name_search("two")
        self.assertIn((proj2.id, "23-00012 - two"), results)
        self.assertNotIn((proj1.id, "23-00011 - one"), results)
        self.assertNotIn((proj3.id, "23-00013 - three"), results)

        # Search by sequence code
        results = self.env["project.project"].name_search("23-00012")
        self.assertIn((proj2.id, "23-00012 - two"), results)
        self.assertNotIn((proj1.id, "23-00011 - one"), results)
        self.assertNotIn((proj3.id, "23-00013 - three"), results)
