# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProjectSubManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sub_manager = cls.env["res.users"].create(
            {
                "name": "Sub Manager",
                "login": "sub_manager_project_sub_manager",
                "email": "sub_manager_project_sub_manager@example.com",
            }
        )
        cls.project = cls.env["project.project"].create({"name": "Test Project"})

    def test_auto_subscribe_sub_managers(self):
        self.project.write({"sub_manager_ids": [(6, 0, [self.sub_manager.id])]})
        self.assertIn(self.sub_manager.partner_id, self.project.message_partner_ids)

    def test_no_auto_subscribe_without_sub_manager_change(self):
        res = self.project._message_auto_subscribe_followers({"name": "x"}, [1])
        self.assertEqual(res, [])

    def test_auto_subscribe_sub_managers_empty(self):
        res = self.project._message_auto_subscribe_followers(
            {"sub_manager_ids": [(6, 0, [])]}, [1]
        )
        self.assertEqual(res, [])

    def test_auto_subscribe_sub_managers_direct(self):
        res = self.project._message_auto_subscribe_followers(
            {"sub_manager_ids": [(6, 0, [self.sub_manager.id])]}, [1]
        )
        self.assertIn((self.sub_manager.partner_id.id, [1], False), res)
