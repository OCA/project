# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.base.tests.common import BaseCommon


class TestTaskStageOrderCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.Project = cls.env["project.project"]
        cls.Stage = cls.env["project.task.type"]
        cls.Sequence = cls.env["project.task.type.sequence"]
        cls.Task = cls.env["project.task"]
        # Setup
        cls.env.company.task_stage_order_enabled = True
        # Instances
        cls.project_a = cls._create_project(name="Test Project A")
        cls.project_b = cls._create_project(name="Test Project B")
        cls.stage_new = cls._create_stage(
            name="Test New Stage",
            sequence=1,
            project_ids=[(6, 0, [cls.project_a.id, cls.project_b.id])],
        )
        cls.stage_done = cls._create_stage(
            name="Test Done Stage",
            sequence=2,
            project_ids=[(6, 0, [cls.project_a.id, cls.project_b.id])],
        )

    @classmethod
    def _create_project(cls, **kwargs):
        return cls.Project.create(kwargs)

    @classmethod
    def _create_stage(cls, **kwargs):
        return cls.Stage.create(kwargs)

    def _sequence_for(self, project, stage):
        return self.Sequence.search(
            [("project_id", "=", project.id), ("stage_id", "=", stage.id)]
        )
