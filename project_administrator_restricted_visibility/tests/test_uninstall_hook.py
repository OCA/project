# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon

from ..hooks import uninstall_hook


class TestUninstallHook(BaseCommon):
    _test_user_groups = None

    def test_01_uninstall_hook(self):
        restricted_group = self.env.ref("project.group_project_manager")
        manager_rule = self.env.ref("project.project_project_manager_rule")
        task_manager_rule = self.env.ref(
            "project.project_manager_all_project_tasks_rule"
        )
        # The original accesses are kept for the administrator group
        self.assertEqual(manager_rule.group_id, restricted_group)
        self.assertEqual(task_manager_rule.group_id, restricted_group)
        self.assertEqual(restricted_group.name, "Restricted Administrator")

        uninstall_hook(self.env)

        # Checks if the group name has been reset
        self.assertEqual(restricted_group.name, "Administrator")
