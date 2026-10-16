from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import TestTaskStageOrderCommon


@tagged("-at_install", "post_install")
class TestTaskStageOrder(TestTaskStageOrderCommon):
    def test_sequence_rows_created_on_stage_creation(self):
        row_a = self._sequence_for(self.project_a, self.stage_new)
        row_b = self._sequence_for(self.project_b, self.stage_new)
        self.assertTrue(row_a)
        self.assertTrue(row_b)

    def test_reorder_within_project_is_isolated(self):
        self.stage_new.with_context(default_project_id=self.project_a.id).write(
            {"sequence": 50}
        )
        row_a = self._sequence_for(self.project_a, self.stage_new)
        row_b = self._sequence_for(self.project_b, self.stage_new)
        self.assertEqual(row_a.sequence, 50)
        self.assertNotEqual(row_b.sequence, 50)
        self.assertNotEqual(self.stage_new.sequence, 50)

    def test_reorder_from_configuration_pushes_to_all_projects(self):
        self.stage_new.write({"sequence": 80})
        row_a = self._sequence_for(self.project_a, self.stage_new)
        row_b = self._sequence_for(self.project_b, self.stage_new)
        self.assertEqual(row_a.sequence, 80)
        self.assertEqual(row_b.sequence, 80)

    def test_create_duplicate_name_merges_into_existing_stage(self):
        project_c = self.Project.create({"name": "Test Project C"})
        count_before = self.Stage.search_count([("name", "=", "Test New Stage")])
        self.Stage.create(
            {
                "name": "Test New Stage",
                "project_ids": [(6, 0, [project_c.id])],
            }
        )
        count_after = self.Stage.search_count([("name", "=", "Test New Stage")])
        self.assertEqual(count_before, count_after)
        self.assertIn(project_c, self.stage_new.project_ids)

    def test_unlink_blocked_when_tasks_exist(self):
        self.Task.create(
            {
                "name": "Test Task",
                "project_id": self.project_a.id,
                "stage_id": self.stage_new.id,
            }
        )
        row = self._sequence_for(self.project_a, self.stage_new)
        with self.assertRaises(UserError):
            row.unlink()

    def test_unlink_removes_project_and_cleans_up_orphan_stage(self):
        project_only = self.Project.create({"name": "Test Project Only"})
        stage_only = self.Stage.create(
            {
                "name": "Test Only Stage",
                "project_ids": [(6, 0, [project_only.id])],
            }
        )
        row = self._sequence_for(project_only, stage_only)
        row.unlink()
        self.assertFalse(stage_only.exists())
