# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestProjectTags(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag_1 = cls.env["project.tags"].create({"name": "tag1"})
        cls.tag_2 = cls.env["project.tags"].create({"name": "tag2"})

        cls.project1 = cls.env["project.project"].create(
            {"name": "Project 1", "tag_ids": [6, 0, cls.tag_1.id]}
        )
        cls.task1 = cls.env["project.task"].create(
            {"name": "name1", "project_id": cls.project1.id}
        )

    def test_tags_on_task(self):
        self.assertEqual(len(self.project1.tag_ids), 1)
        self.project1.write({"tag_ids": [4, 0, [self.tag_2.id]]})
        self.assertEqual(len(self.project1.tag_ids), 2)
        results = self.task1.tag_ids.name_search()
        self.assertIn(self.tag_1.id, results)
        self.assertIn(self.tag_2.id, results)

        # remove tag from project
        self.project1.write({"tag_ids", [3, 0, [self.tag_1.id]]})
        results = self.task1.tag_ids.name_search()
        self.assertNotIn(self.tag_1.id, results)
        self.assertIn(self.tag_2.id, results)
