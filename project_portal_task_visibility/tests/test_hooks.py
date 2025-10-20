from odoo.tests.common import TransactionCase

from ..hooks import post_init_hook, uninstall_hook


class TestHooks(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule = "project.project_task_rule_portal"

    def test_post_init_hook(self):
        post_init_hook(self.env)
        self.assertFalse(self.env.ref(self.rule).active)

    def test_uninstall_hook(self):
        uninstall_hook(self.env.cr, self.env.registry)
        self.assertTrue(self.env.ref(self.rule).active)
