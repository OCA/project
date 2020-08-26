# Copyright 2020 haulogy SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectParent(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project_project_1 = self.browse_ref("project.project_project_1")
        self.project_project_2 = self.browse_ref("project.project_project_2")
        self.project_project_3 = self.env["project.project"].create(
            {"name": "TestProject", "parent_id": self.project_project_1.id}
        )

    def test_parent_childs_project(self):
        self.assertTrue(self.project_project_2 in self.project_project_1.child_ids)
        self.assertTrue(self.project_project_3 in self.project_project_1.child_ids)

    def test_action_open_child_project(self):
        res = self.project_project_1.action_open_child_project()
        self.assertEquals(
            res.get("domain"), [("parent_id", "=", self.project_project_1.id)]
        )
        self.assertEquals(
            res.get("context").get("default_parent_id"), self.project_project_1.id
        )
