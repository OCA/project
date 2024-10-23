# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase

from ..hooks import uninstall_hook


class TestUninstallHook(TransactionCase):
    def test_01_uninstall_hook(self):
        restricted_group = self.env.ref("project.group_project_manager")
        full_group = self.env.ref(
            "project_administrator_restricted_visibility.group_full_project_manager"
        )
        manager_rule = self.env.ref("project.project_project_manager_rule")
        # Checks Restricted Administrator Group has not project manager rule
        self.assertFalse(
            any(set(restricted_group.rule_groups.ids) & set(manager_rule.ids))
        )
        # Checks Full Administrator Group has project manager rule
        self.assertTrue(any(set(full_group.rule_groups.ids) & set(manager_rule.ids)))

        uninstall_hook(self.env.cr, False)

        # Checks if the rules have been reset
        self.assertTrue(
            any(set(restricted_group.rule_groups.ids) & set(manager_rule.ids))
        )
        self.assertFalse(any(set(full_group.rule_groups.ids) & set(manager_rule.ids)))
