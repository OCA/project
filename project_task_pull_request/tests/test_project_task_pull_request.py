# Copyright 2017 Specialty Medical Drugstore
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProjectTaskPullRequest(TransactionCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(TestProjectTaskPullRequest, self).setUp()

        project_obj = self.env["project.project"]
        task_obj = self.env["project.task"]
        stages = self.env["project.task.type"]
        self.stage1 = stages.create({"name": "a"})
        self.stage3 = stages.create({"name": "c"})
        self.stage4 = stages.create({"name": "f"})
        self.done_stage = stages.create({"name": "d"})
        self.inprogress_stage = stages.create({"name": "e"})

        self.project_1 = project_obj.create(
            {"name": "Test Project 1", "pr_required_states": [(4, self.done_stage.id)]}
        )
        self.project_2 = project_obj.create(
            {
                "name": "Test Project 2",
                "pr_required_states": [
                    (4, self.done_stage.id),
                    (4, self.inprogress_stage.id),
                ],
            }
        )

        self.task_1 = task_obj.create(
            {
                "name": "Test Task 1",
                "project_id": self.project_1.id,
                "pr_uri": False,
                "stage_id": self.stage1.id,
            }
        )
        self.task_2 = task_obj.create(
            {
                "name": "Test Task 2",
                "project_id": self.project_2.id,
                "pr_uri": False,
                "stage_id": self.stage1.id,
            }
        )
        self.task_3 = task_obj.create(
            {
                "name": "Test Task 3",
                "project_id": self.project_2.id,
                "pr_uri": "github.com",
                "stage_id": self.stage1.id,
            }
        )

    def test_write_allowed_when_allowed(self):
        self.task_1.write({"stage_id": self.stage3.id})
        self.task_1.refresh()
        self.assertEqual(self.stage3.id, self.task_1.stage_id.id)

    def test_write_not_allowed_without_pr(self):
        with self.assertRaises(ValidationError):
            self.task_1.write({"stage_id": self.done_stage.id})

    def test_write_not_allowed_without_pr_multiple_stages(self):
        with self.assertRaises(ValidationError):
            self.task_2.write({"stage_id": self.inprogress_stage.id})

    def test_write_allowed_with_pr(self):
        self.task_3.write({"stage_id": self.stage4.id})
        self.task_3.refresh()
        self.assertEqual(self.stage4.id, self.task_3.stage_id.id)
