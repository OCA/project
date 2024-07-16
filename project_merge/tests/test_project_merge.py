from odoo.addons.project.tests.test_project_base import TestProjectCommon


class TestProjectMerge(TestProjectCommon):
    @classmethod
    def setUpClass(cls):
        super(TestProjectMerge, cls).setUpClass()
        cls.ProjectMerge = cls.env["project.task.merge"]

    def test_project_task_merge_create_new_task(self):
        self.task_merge_1 = self.ProjectMerge.with_context(
            active_ids=[self.task_1.id, self.task_2.id]
        ).create({"create_new_task": True, "dst_task_name": "Test 1"})
        self.task_merge_1.merge_tasks()
        self.assertEqual(self.task_merge_1.dst_task_id.name, "Test 1")

    def test_project_task_merge_with_existing_ticket(self):
        self.task_merge_2 = self.ProjectMerge.with_context(
            active_ids=[self.task_1.id, self.task_2.id]
        ).create({})
        self.task_merge_2.merge_tasks()
        self.assertEqual(self.task_merge_2.dst_task_id.name, "Pigs UserTask")
