from odoo.tests.common import TransactionCase

from ..hooks import post_init_hook, uninstall_hook, views_to_switch


class TestHooks(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.views = (
            cls.env["ir.ui.view"]
            .with_context(active_test=False)
            .search([("key", "in", views_to_switch)])
        )

    def test_post_init_hook(self):
        views = self.views
        self.assertTrue(views)
        post_init_hook(self.env.cr, self.env.registry)
        self.assertTrue(all(not v.active for v in views))

    def test_uninstall_hook(self):
        views = self.views
        self.assertTrue(views)
        uninstall_hook(self.env.cr, self.env.registry)
        self.assertTrue(all(v.active for v in views))
