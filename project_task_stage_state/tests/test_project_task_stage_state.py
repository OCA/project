# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestProjectTaskStageState(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stage_new = cls.env.ref("project.project_stage_0")
        cls.stage_in_progress = cls.env.ref("project.project_stage_1")
        cls.stage_done = cls.env.ref("project.project_stage_2")
        cls.stage_canceled = cls.env.ref("project.project_stage_3")
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test task",
                "project_id": cls.env.ref("project.project_project_1").id,
                "stage_id": cls.stage_new.id,
                "state": "01_in_progress",
            }
        )

    def test_project_task_stages(self):
        # Change to done: the state is changed
        self.task.write({"stage_id": self.stage_done.id})
        self.assertEqual(self.task.state, "1_done")
        # Change to cancelled: the state is changed
        self.task.write({"stage_id": self.stage_canceled.id})
        self.assertEqual(self.task.state, "1_canceled")
        # Change to new: the state is NOT changed
        self.task.write({"stage_id": self.stage_new.id})
        self.assertEqual(self.task.state, "1_canceled")
        # Change to in progress: the state is changed
        self.task.write({"stage_id": self.stage_in_progress.id})
        self.assertEqual(self.task.state, "01_in_progress")
