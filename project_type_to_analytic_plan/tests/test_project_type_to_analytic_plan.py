# Copyright 2026 Innovyou - Lorenzo Battistini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProjectTypeToAnalyticPlan(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AnalyticPlan = cls.env["account.analytic.plan"]
        cls.AnalyticAccount = cls.env["account.analytic.account"]
        cls.ProjectType = cls.env["project.type"]
        cls.Project = cls.env["project.project"]

        cls.root_plan = cls.AnalyticPlan.create({"name": "Project Types Root"})
        cls.other_plan = cls.AnalyticPlan.create({"name": "Other Plan"})
        cls.env.company.project_types_root_analytic_plan_id = cls.root_plan

    def _new_account(self, name, plan=None):
        return self.AnalyticAccount.create(
            {"name": name, "plan_id": (plan or self.other_plan).id}
        )

    def _new_project(self, name, type_=None):
        """Create a project and let the standard project module create its
        analytic account (on the default analytic project plan)."""
        project = self.Project.create(
            {"name": name, "type_id": type_.id if type_ else False}
        )
        project._create_analytic_account()
        return project

    def _plan_of(self, project_type):
        return self.AnalyticPlan.search(
            [("project_type_id", "=", project_type.id)], limit=1
        )

    # ---------------------------------------------------------------
    # Automatic sync on project.type create / write / unlink
    # ---------------------------------------------------------------

    def test_create_project_type_creates_plan(self):
        pt = self.ProjectType.create({"name": "Internal"})
        plan = self._plan_of(pt)
        self.assertTrue(plan)
        self.assertEqual(plan.name, "Internal")
        self.assertEqual(plan.parent_id, self.root_plan)
        self.assertEqual(pt.analytic_plan_id, plan)

    def test_create_child_project_type_uses_parent_plan(self):
        parent = self.ProjectType.create({"name": "Internal"})
        child = self.ProjectType.create({"name": "R&D", "parent_id": parent.id})
        self.assertEqual(child.analytic_plan_id.parent_id, parent.analytic_plan_id)

    def test_create_project_type_no_root_plan_skips_sync(self):
        self.env.company.project_types_root_analytic_plan_id = False
        pt = self.ProjectType.create({"name": "Orphan"})
        self.assertFalse(self._plan_of(pt))

    def test_create_project_type_not_project_ok_skips_sync(self):
        pt = self.ProjectType.create(
            {"name": "Tasks Only", "project_ok": False, "task_ok": True}
        )
        self.assertFalse(self._plan_of(pt))

    def test_rename_project_type_renames_plan(self):
        pt = self.ProjectType.create({"name": "Internal"})
        pt.name = "Internal Renamed"
        self.assertEqual(pt.analytic_plan_id.name, "Internal Renamed")

    def test_move_project_type_moves_plan(self):
        parent_a = self.ProjectType.create({"name": "A"})
        parent_b = self.ProjectType.create({"name": "B"})
        child = self.ProjectType.create({"name": "Child", "parent_id": parent_a.id})
        self.assertEqual(child.analytic_plan_id.parent_id, parent_a.analytic_plan_id)
        child.parent_id = parent_b
        self.assertEqual(child.analytic_plan_id.parent_id, parent_b.analytic_plan_id)

    def test_unset_parent_moves_plan_to_root(self):
        parent = self.ProjectType.create({"name": "Parent"})
        child = self.ProjectType.create({"name": "Child", "parent_id": parent.id})
        child.parent_id = False
        self.assertEqual(child.analytic_plan_id.parent_id, self.root_plan)

    def test_delete_project_type_deletes_plan(self):
        pt = self.ProjectType.create({"name": "Temp"})
        plan = pt.analytic_plan_id
        self.assertTrue(plan.exists())
        pt.unlink()
        self.assertFalse(plan.exists())

    def test_delete_project_type_with_projects_blocked(self):
        pt = self.ProjectType.create({"name": "InUse"})
        self._new_project("P", type_=pt)
        with self.assertRaises(UserError):
            pt.unlink()

    def test_delete_project_type_with_accounts_blocked(self):
        pt = self.ProjectType.create({"name": "WithAcc"})
        self._new_account("AA", plan=pt.analytic_plan_id)
        with self.assertRaises(UserError):
            pt.unlink()

    # ---------------------------------------------------------------
    # project_ok toggle
    # ---------------------------------------------------------------

    def test_project_ok_toggle_off_deletes_plan(self):
        pt = self.ProjectType.create({"name": "Toggle"})
        plan = pt.analytic_plan_id
        self.assertTrue(plan.exists())
        pt.project_ok = False
        self.assertFalse(plan.exists())

    def test_project_ok_toggle_off_blocked_when_accounts(self):
        pt = self.ProjectType.create({"name": "Toggle"})
        self._new_account("AA", plan=pt.analytic_plan_id)
        with self.assertRaises(UserError):
            pt.project_ok = False

    def test_project_ok_toggle_on_creates_plan(self):
        pt = self.ProjectType.create(
            {"name": "TaskOnly", "project_ok": False, "task_ok": True}
        )
        self.assertFalse(self._plan_of(pt))
        pt.project_ok = True
        self.assertTrue(self._plan_of(pt))

    # ---------------------------------------------------------------
    # project.project synchronization
    # ---------------------------------------------------------------

    def test_project_type_assignment_links_account(self):
        pt = self.ProjectType.create({"name": "Internal"})
        project = self._new_project("P1")
        self.assertNotEqual(project.account_id.plan_id, pt.analytic_plan_id)
        project.type_id = pt
        self.assertEqual(project.account_id.plan_id, pt.analytic_plan_id)

    def test_project_type_change_relinks_account(self):
        pt_a = self.ProjectType.create({"name": "A"})
        pt_b = self.ProjectType.create({"name": "B"})
        project = self._new_project("P1", type_=pt_a)
        self.assertEqual(project.account_id.plan_id, pt_a.analytic_plan_id)
        project.type_id = pt_b
        self.assertEqual(project.account_id.plan_id, pt_b.analytic_plan_id)

    # ---------------------------------------------------------------
    # Read-only constraints on synchronized plans and accounts
    # ---------------------------------------------------------------

    def test_synced_plan_rename_blocked(self):
        pt = self.ProjectType.create({"name": "Internal"})
        with self.assertRaises(UserError):
            pt.analytic_plan_id.name = "Hacked"

    def test_synced_plan_reparent_blocked(self):
        pt = self.ProjectType.create({"name": "Internal"})
        with self.assertRaises(UserError):
            pt.analytic_plan_id.parent_id = self.other_plan

    def test_synced_plan_unlink_with_accounts_blocked(self):
        pt = self.ProjectType.create({"name": "Internal"})
        self._new_account("AA", plan=pt.analytic_plan_id)
        with self.assertRaises(UserError):
            pt.analytic_plan_id.unlink()

    def test_synced_account_change_plan_blocked(self):
        pt = self.ProjectType.create({"name": "Internal"})
        aa = self._new_account("AA", plan=pt.analytic_plan_id)
        with self.assertRaises(UserError):
            aa.plan_id = self.other_plan

    def test_synced_account_unlink_blocked(self):
        pt = self.ProjectType.create({"name": "Internal"})
        aa = self._new_account("AA", plan=pt.analytic_plan_id)
        with self.assertRaises(UserError):
            aa.unlink()

    def test_unsynced_plan_modifications_allowed(self):
        self.other_plan.name = "Renamed Freely"
        self.assertEqual(self.other_plan.name, "Renamed Freely")

    def test_unsynced_account_modifications_allowed(self):
        aa = self._new_account("Free")
        free_plan = self.AnalyticPlan.create({"name": "Free Plan"})
        aa.plan_id = free_plan
        self.assertEqual(aa.plan_id, free_plan)

    # ---------------------------------------------------------------
    # Initial sync action
    # ---------------------------------------------------------------

    def test_action_sync_requires_root_plan(self):
        self.env.company.project_types_root_analytic_plan_id = False
        settings = self.env["res.config.settings"].create({})
        with self.assertRaises(UserError):
            settings.action_synchronize_project_types_with_plans()

    def test_action_sync_rebuilds_tree(self):
        # Build types without a root configured, then turn on sync.
        self.env.company.project_types_root_analytic_plan_id = False
        pt_a = self.ProjectType.create({"name": "A"})
        pt_b = self.ProjectType.create({"name": "B", "parent_id": pt_a.id})
        project = self._new_project("P", type_=pt_b)
        original_plan = project.account_id.plan_id

        new_root = self.AnalyticPlan.create({"name": "Sync Root"})
        self.env.company.project_types_root_analytic_plan_id = new_root
        settings = self.env["res.config.settings"].create({})
        settings.action_synchronize_project_types_with_plans()

        plan_a = self._plan_of(pt_a)
        plan_b = self._plan_of(pt_b)
        self.assertTrue(plan_a)
        self.assertTrue(plan_b)
        self.assertEqual(plan_a.parent_id, new_root)
        self.assertEqual(plan_b.parent_id, plan_a)
        self.assertNotEqual(original_plan, plan_b)
        # Project's analytic account has been moved under the matching plan
        self.assertEqual(project.account_id.plan_id, plan_b)
