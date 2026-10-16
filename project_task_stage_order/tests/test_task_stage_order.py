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

    def test_stage_unlink_redirects_when_multiple_projects(self):
        self.stage_new.with_context(default_project_id=self.project_a.id).unlink()
        self.assertTrue(self.stage_new.exists())
        self.assertNotIn(self.project_a, self.stage_new.project_ids)
        self.assertIn(self.project_b, self.stage_new.project_ids)

    def test_stage_unlink_deletes_when_only_project(self):
        project_only = self.Project.create({"name": "Test Project Only Delete"})
        stage_only = self.Stage.create(
            {
                "name": "Test Solo Stage",
                "project_ids": [(6, 0, [project_only.id])],
            }
        )
        stage_only.with_context(default_project_id=project_only.id).unlink()
        self.assertFalse(stage_only.exists())

    def test_stage_unlink_archives_when_tasks_exist(self):
        project_only = self.Project.create({"name": "Test Project With Task"})
        stage_only = self.Stage.create(
            {
                "name": "Test Stage With Task",
                "project_ids": [(6, 0, [project_only.id])],
            }
        )
        self.Task.create(
            {
                "name": "Test Task",
                "project_id": project_only.id,
                "stage_id": stage_only.id,
            }
        )
        stage_only.with_context(default_project_id=project_only.id).unlink()
        self.assertTrue(stage_only.exists())
        self.assertFalse(stage_only.active)

    def test_removing_project_from_stage_cleans_up_sequence_row(self):
        self.stage_new.write({"project_ids": [(3, self.project_b.id)]})
        row_b = self._sequence_for(self.project_b, self.stage_new)
        self.assertFalse(row_b)
        self.assertNotIn(self.project_b, self.stage_new.project_ids)

    def test_create_sequence_row_directly_links_project_to_stage(self):
        project_d = self.Project.create({"name": "Test Project D"})
        self.Sequence.create(
            {
                "project_id": project_d.id,
                "stage_id": self.stage_new.id,
                "sequence": 5,
            }
        )
        self.assertIn(project_d, self.stage_new.project_ids)

    def test_kanban_order_reflects_project_sequence(self):
        self._sequence_for(self.project_a, self.stage_new).sequence = 100
        self._sequence_for(self.project_a, self.stage_done).sequence = 1
        ordered = self.Task.with_context(
            default_project_id=self.project_a.id
        )._read_group_stage_ids(self.stage_new | self.stage_done, [])
        self.assertEqual(list(ordered), [self.stage_done, self.stage_new])
