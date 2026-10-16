from odoo.tests.common import TransactionCase


class TestTaskStageOrderCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.Stage = cls.env["project.task.type"]
        cls.Sequence = cls.env["project.task.type.sequence"]
        cls.Task = cls.env["project.task"]

        cls.env.company.task_stage_order_enabled = True

        cls.project_a = cls.Project.create({"name": "Test Project A"})
        cls.project_b = cls.Project.create({"name": "Test Project B"})

        cls.stage_new = cls.Stage.create(
            {
                "name": "Test New Stage",
                "sequence": 1,
                "project_ids": [(6, 0, [cls.project_a.id, cls.project_b.id])],
            }
        )
        cls.stage_done = cls.Stage.create(
            {
                "name": "Test Done Stage",
                "sequence": 2,
                "project_ids": [(6, 0, [cls.project_a.id, cls.project_b.id])],
            }
        )

    def _sequence_for(self, project, stage):
        return self.Sequence.search(
            [("project_id", "=", project.id), ("stage_id", "=", stage.id)]
        )
