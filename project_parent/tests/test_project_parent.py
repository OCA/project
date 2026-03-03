# Copyright 2020 haulogy SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestProjectParent(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Project = cls.env["project.project"]
        cls.project_project_1 = Project.create({"name": "TestProject 1"})
        cls.project_project_2 = Project.create({"name": "TestProject 2"})
        cls.project_project_3 = Project.create(
            {"name": "TestProject", "parent_id": cls.project_project_1.id}
        )

    def test_parent_childs_project(self):
        self.assertNotIn(self.project_project_2, self.project_project_1.child_ids)
        self.assertIn(self.project_project_3, self.project_project_1.child_ids)

    def test_action_open_child_project(self):
        res = self.project_project_1.action_open_child_project()
        self.assertEqual(
            res.get("domain"), [("parent_id", "=", self.project_project_1.id)]
        )
        self.assertEqual(
            res.get("context").get("default_parent_id"), self.project_project_1.id
        )
