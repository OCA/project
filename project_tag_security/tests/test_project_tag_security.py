# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTagSecurity(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_1 = cls.env["project.project"].create({"name": "Test project 1"})
        cls.project_2 = cls.env["project.project"].create({"name": "Test project 2"})
        cls.project_3 = cls.env["project.project"].create({"name": "Test project 3"})
        cls.tag_1 = cls.env["project.tags"].create({"name": "Tag 1"})
        cls.tag_2 = cls.env["project.tags"].create(
            {"name": "Tag 2", "allowed_project_ids": [(6, 0, [cls.project_1.id])]}
        )
        cls.tag_3 = cls.env["project.tags"].create(
            {
                "name": "Tag 3",
                "allowed_project_ids": [(6, 0, [cls.project_1.id, cls.project_2.id])],
            }
        )

    def _get_project_tags(self, project_id):
        """We obtain tags with a domain similar to the one set in the form views of
        project and tasks.
        """
        return self.env["project.tags"].search(
            [
                "|",
                ("allowed_project_ids", "in", [project_id]),
                ("allowed_project_ids", "=", False),
            ]
        )

    def test_project_tags_01(self):
        tags = self._get_project_tags(self.project_1.id)
        self.assertIn(self.tag_1, tags)
        self.assertIn(self.tag_2, tags)
        self.assertIn(self.tag_3, tags)

    def test_project_tags_02(self):
        tags = self._get_project_tags(self.project_2.id)
        self.assertIn(self.tag_1, tags)
        self.assertNotIn(self.tag_2, tags)
        self.assertIn(self.tag_3, tags)

    def test_project_tags_03(self):
        tags = self._get_project_tags(self.project_3.id)
        self.assertIn(self.tag_1, tags)
        self.assertNotIn(self.tag_2, tags)
        self.assertNotIn(self.tag_3, tags)
