# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTaskStageStateSync(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.stage_in_progress = cls.env["project.task.type"].create(
            {
                "name": "In Progress",
                "sequence": 1,
                "task_state": "01_in_progress",
                "project_ids": [(4, cls.project.id)],
            }
        )
        cls.stage_done = cls.env["project.task.type"].create(
            {
                "name": "Done",
                "sequence": 2,
                "task_state": "1_done",
                "sync_state_to_stage": True,
                "project_ids": [(4, cls.project.id)],
            }
        )
        cls.stage_canceled = cls.env["project.task.type"].create(
            {
                "name": "Canceled",
                "sequence": 3,
                "task_state": "1_canceled",
                "sync_state_to_stage": False,
                "project_ids": [(4, cls.project.id)],
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
                "stage_id": cls.stage_in_progress.id,
            }
        )

    def test_state_change_moves_task_to_synced_stage(self):
        self.task.write({"state": "1_done"})
        self.assertEqual(self.task.state, "1_done")
        self.assertEqual(self.task.stage_id, self.stage_done)

    def test_no_sync_when_checkbox_disabled(self):
        self.task.write({"state": "1_canceled"})
        self.assertNotEqual(self.task.stage_id, self.stage_canceled)
        self.assertEqual(self.task.stage_id, self.stage_in_progress)

    def test_no_matching_stage_is_noop(self):
        self.task.write({"state": "04_waiting_normal"})
        self.assertEqual(self.task.stage_id, self.stage_in_progress)

    def test_constraint_raises_on_duplicate_sync(self):
        project = self.env["project.project"].create({"name": "Constraint Test"})
        self.env["project.task.type"].create(
            {
                "name": "Done A",
                "task_state": "1_done",
                "sync_state_to_stage": True,
                "project_ids": [(4, project.id)],
            }
        )
        with self.assertRaises(ValidationError):
            self.env["project.task.type"].create(
                {
                    "name": "Done B",
                    "task_state": "1_done",
                    "sync_state_to_stage": True,
                    "project_ids": [(4, project.id)],
                }
            )

    def test_constraint_allows_same_state_without_sync(self):
        project = self.env["project.project"].create({"name": "Constraint Test"})
        self.env["project.task.type"].create(
            {
                "name": "Done A",
                "task_state": "1_done",
                "sync_state_to_stage": True,
                "project_ids": [(4, project.id)],
            }
        )
        self.env["project.task.type"].create(
            {
                "name": "Done B",
                "task_state": "1_done",
                "sync_state_to_stage": False,
                "project_ids": [(4, project.id)],
            }
        )

    def test_constraint_allows_sync_without_task_state(self):
        # sync_state_to_stage=True with no task_state set is never a conflict.
        self.env["project.task.type"].create(
            {
                "name": "Unmapped Stage",
                "sync_state_to_stage": True,
            }
        )
