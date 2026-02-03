# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.base.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProjectTagHierarchy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag_1 = cls.env["project.tags"].create({"name": "Tag 1"})
        cls.tag_2 = cls.env["project.tags"].create(
            {"name": "Tag 2", "parent_id": cls.tag_1.id}
        )
        cls.tag_3 = cls.env["project.tags"].create(
            {"name": "Tag 3", "parent_id": cls.tag_2.id}
        )

    def test_project_tag_display_name(self):
        self.assertEqual(self.tag_1.display_name, "Tag 1")
        self.assertEqual(self.tag_2.display_name, "Tag 1 / Tag 2")
        self.assertEqual(self.tag_3.display_name, "Tag 1 / Tag 2 / Tag 3")

    def test_project_tag_recursion(self):
        with self.assertRaises(UserError):
            self.tag_1.parent_id = self.tag_3
