# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon

from ..hooks import uninstall_hook


class TestUninstallHook(BaseCommon):
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_restricted_padmin = new_test_user(
            cls.env,
            login="restricted-project-admin",
            groups="project.group_project_manager",
        )
        cls.restricted_project = cls.env["project.project"].create(
            {
                "name": "Restricted project",
                "privacy_visibility": "followers",
                "user_id": cls.env.ref("base.user_admin").id,
            }
        )
        cls.restricted_task = cls.env["project.task"].create(
            {
                "name": "Private task",
                "project_id": cls.restricted_project.id,
                "user_ids": [(6, 0, cls.env.ref("base.user_admin").ids)],
            }
        )

    def _visible_as_restricted_admin(self):
        env = self.env(user=self.user_restricted_padmin)
        return (
            self.restricted_project in env["project.project"].search([]),
            self.restricted_task in env["project.task"].search([]),
        )

    def test_01_uninstall_hook(self):
        restricted_group = self.env.ref("project.group_project_manager")
        project_rule = self.env.ref(
            "project_administrator_restricted_visibility.project_restricted_manager_rule"
        )
        task_rule = self.env.ref(
            "project_administrator_restricted_visibility.task_restricted_manager_rule"
        )
        self.assertTrue(project_rule.active)
        self.assertTrue(task_rule.active)
        self.assertEqual(restricted_group.name, "Restricted Administrator")
        self.assertEqual(self._visible_as_restricted_admin(), (False, False))

        uninstall_hook(self.env)

        # The restrictions are lifted and the group name is restored
        self.assertFalse(project_rule.active)
        self.assertFalse(task_rule.active)
        self.assertEqual(restricted_group.name, "Administrator")
        self.assertEqual(self._visible_as_restricted_admin(), (True, True))
