# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTagHierarchy(BaseCommon):
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

    def test_project_tag_name_get(self):
        tag_1_name = self.tag_1.name_get()
        self.assertEqual(tag_1_name[0][1], "Tag 1")
        tag_2_name = self.tag_2.name_get()
        self.assertEqual(tag_2_name[0][1], "Tag 1 / Tag 2")
        tag_3_name = self.tag_3.name_get()
        self.assertEqual(tag_3_name[0][1], "Tag 1 / Tag 2 / Tag 3")
