from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestParentChildBlock(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "privacy_visibility": "employees",
                "alias_name": "project+test",
            }
        )
        cls.parent_task = cls.env["project.task"].create(
            {"name": "Pigs UserTask", "project_id": cls.test_project.id}
        )
        cls.child_task = cls.env["project.task"].create(
            {"name": "Pigs ManagerTask", "project_id": cls.test_project.id}
        )

        cls.stage_pending = cls.env["project.task.type"].create(
            {"name": "a", "project_ids": [(4, cls.test_project.id)], "fold": False}
        )
        cls.stage_done = cls.env["project.task.type"].create(
            {"name": "b", "project_ids": [(4, cls.test_project.id)], "fold": True}
        )
        cls.child_task.parent_id = cls.parent_task
        cls.parent_task.stage_id = cls.stage_pending
        cls.child_task.stage_id = cls.stage_pending

    def test_child_blocks_parent(self):
        with self.assertRaises(ValidationError):
            self.parent_task.stage_id = self.stage_done
        extra_task = self.env["project.task"].create(
            {
                "name": "Test Task 3",
                "project_id": self.test_project.id,
            }
        )
        self.parent_task.child_ids += extra_task
        extra_task.stage_id = self.stage_done
        with self.assertRaises(ValidationError):
            self.parent_task.stage_id = self.stage_done

    def test_child_not_blocks_parent(self):
        self.child_task.stage_id = self.stage_done
        self.parent_task.stage_id = self.stage_done
        self.assertEqual(
            self.parent_task.stage_id,
            self.stage_done,
            "Parent should be done if child is done",
        )
