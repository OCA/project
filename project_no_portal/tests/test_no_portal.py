# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.project_no_portal.hooks import post_init_hook, uninstall_hook


class TestProjectNoPortal(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.company
        # The block is opt-in (off by default); enable it for the company so the
        # blocking tests exercise the feature. The "company allows" tests flip it
        # back off.
        cls.company.block_project_portal_access = True
        cls.portal_group = cls.env.ref("base.group_portal")
        cls.portal_partner = cls.env["res.partner"].create(
            {
                "name": "Portal Tester Partner",
                "email": "portal.tester@example.com",
            }
        )
        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Portal Tester",
                "login": "portal.tester@example.com",
                "partner_id": cls.portal_partner.id,
                "company_id": cls.company.id,
                "company_ids": [(6, 0, [cls.company.id])],
                "groups_id": [(6, 0, [cls.portal_group.id])],
            }
        )

        cls.project = cls.env["project.project"].create(
            {
                "name": "Test No Portal Project",
                "privacy_visibility": "employees",
                "company_id": cls.company.id,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test No Portal Task",
                "project_id": cls.project.id,
            }
        )

        cls.PortalProject = cls.env["project.project"].with_user(cls.portal_user)
        cls.PortalTask = cls.env["project.task"].with_user(cls.portal_user)

    def _set_block(self, enabled):
        self.company.block_project_portal_access = enabled

    def _force_portal_visibility(self):
        """Set privacy_visibility='portal'.
        Use raw SQL to bypass the python constraint."""
        self.env.cr.execute(
            "UPDATE project_project SET privacy_visibility=%s WHERE id=%s",
            ("portal", self.project.id),
        )
        self.env.invalidate_all()

    def _follow_as_portal(self):
        self.project.message_subscribe(partner_ids=[self.portal_partner.id])
        self.task.message_subscribe(partner_ids=[self.portal_partner.id])

    # --- company blocks -----------------------------------------------------

    def test_block_on_constraint_rejects_portal_visibility(self):
        with self.assertRaises(ValidationError):
            self.env["project.project"].create(
                {
                    "name": "Portal",
                    "privacy_visibility": "portal",
                    "company_id": self.company.id,
                }
            )

    def test_default_visibility_is_employees(self):
        project = self.env["project.project"].create({"name": "Default Visibility"})
        self.assertEqual(project.privacy_visibility, "employees")

    def test_block_on_share_wizard_raises(self):
        with self.assertRaises(UserError):
            self.project.action_open_share_project_wizard()

    def _open_portal_share(self, record):
        return (
            self.env["portal.share"]
            .with_context(active_model=record._name, active_id=record.id)
            .default_get(["res_model", "res_id", "share_link"])
        )

    def test_block_on_task_portal_share_wizard_raises(self):
        # The kanban "Share Task" link opens portal.share directly, bypassing
        # the action-binding removal; default_get must reject it when blocked.
        with self.assertRaises(UserError):
            self._open_portal_share(self.task)

    def test_block_on_project_portal_share_wizard_raises(self):
        with self.assertRaises(UserError):
            self._open_portal_share(self.project)

    def test_task_portal_share_blocked_flag(self):
        self.assertTrue(self.task.portal_share_blocked)
        self._set_block(False)
        self.task.invalidate_recordset(["portal_share_blocked"])
        self.assertFalse(self.task.portal_share_blocked)

    def test_block_off_task_portal_share_wizard_opens(self):
        self._set_block(False)
        res = self._open_portal_share(self.task)
        self.assertEqual(res.get("res_model"), "project.task")
        self.assertEqual(res.get("res_id"), self.task.id)

    def test_block_on_python_layer_denies_even_with_portal_data(self):
        """Even if a project slips to privacy_visibility='portal' through a path
        that skips the constraint (raw SQL here), the python block denies portal
        users at search and direct-read time."""
        self._force_portal_visibility()
        self._follow_as_portal()

        self.assertFalse(self.PortalProject.search([("id", "=", self.project.id)]))
        self.assertFalse(self.PortalTask.search([("id", "=", self.task.id)]))
        with self.assertRaises(AccessError):
            self.PortalProject.browse(self.project.id).check_access("read")
        with self.assertRaises(AccessError):
            self.PortalTask.browse(self.task.id).check_access("read")

    # --- company allows ------------------------------------------------------

    def test_block_off_share_wizard_opens(self):
        self._set_block(False)
        self.project.privacy_visibility = "portal"
        action = self.project.action_open_share_project_wizard()
        self.assertEqual(action.get("res_model"), "project.share.wizard")

    def test_share_task_action_binding_toggle(self):
        action = self.env.ref("project.portal_share_action")

        self.env["project.task"]._set_share_task_action(False)
        self.assertFalse(action.binding_model_id)

        self.env["project.task"]._set_share_task_action(True)
        self.assertEqual(
            action.binding_model_id, self.env.ref("project.model_project_task")
        )

    def test_share_project_action_binding_toggle(self):
        action = self.env.ref("project.project_share_wizard_action")

        self.env["project.project"]._set_share_project_action(True)
        self.assertEqual(
            action.binding_model_id, self.env.ref("project.model_project_project")
        )

        self.env["project.project"]._set_share_project_action(False)
        self.assertFalse(action.binding_model_id)

    # --- hooks ---------------------------------------------------------------

    def test_post_init_hook_flips_portal_projects(self):
        self._force_portal_visibility()
        post_init_hook(self.env)
        self.project.invalidate_recordset(["privacy_visibility"])
        self.assertEqual(self.project.privacy_visibility, "employees")

    def test_uninstall_hook_restores_actions(self):
        task_action = self.env.ref("project.portal_share_action")
        project_action = self.env.ref("project.project_share_wizard_action")
        self.env["project.task"]._set_share_task_action(False)
        self.env["project.project"]._set_share_project_action(True)

        uninstall_hook(self.env)

        self.assertEqual(
            task_action.binding_model_id, self.env.ref("project.model_project_task")
        )
        self.assertFalse(project_action.binding_model_id)

    def test_block_off_portal_follower_can_access(self):
        """With the company's block off, standard Odoo behaviour is restored: a
        portal follower of a 'portal' project can read it and its tasks. Relies
        on the core portal ACLs still being present (we never deleted them)."""
        self._set_block(False)
        self.project.privacy_visibility = "portal"
        self._follow_as_portal()

        self.assertTrue(self.PortalProject.search([("id", "=", self.project.id)]))
        self.assertTrue(self.PortalTask.search([("id", "=", self.task.id)]))
