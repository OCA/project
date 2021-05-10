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
        self.new_stage = self.ref("project.project_stage_0")
        self.inprogress_stage = self.ref("project.project_stage_1")
        self.done_stage = self.ref("project.project_stage_2")
        self.cancel_stage = self.ref("project.project_stage_3")

        self.project_1 = project_obj.create(
            {"name": "Test Project 1", "pr_required_states": [(4, self.done_stage)]}
        )
        self.project_2 = project_obj.create(
            {
                "name": "Test Project 2",
                "pr_required_states": [
                    (4, self.done_stage),
                    (4, self.inprogress_stage),
                ],
            }
        )

        self.task_1 = task_obj.create(
            {
                "name": "Test Task 1",
                "project_id": self.project_1.id,
                "pr_uri": False,
                "stage_id": self.new_stage,
            }
        )
        self.task_2 = task_obj.create(
            {
                "name": "Test Task 2",
                "project_id": self.project_2.id,
                "pr_uri": False,
                "stage_id": self.new_stage,
            }
        )
        self.task_3 = task_obj.create(
            {
                "name": "Test Task 3",
                "project_id": self.project_2.id,
                "pr_uri": "github.com",
                "stage_id": self.new_stage,
            }
        )

    def test_write_allowed_when_allowed(self):
        self.task_1.write({"stage_id": self.inprogress_stage})
        self.task_1.refresh()
        self.assertEquals(self.inprogress_stage, self.task_1.stage_id.id)

    def test_write_not_allowed_without_pr(self):
        with self.assertRaises(ValidationError):
            self.task_1.write({"stage_id": self.done_stage})

    def test_write_not_allowed_without_pr_multiple_stages(self):
        with self.assertRaises(ValidationError):
            self.task_2.write({"stage_id": self.inprogress_stage})

    def test_write_allowed_with_pr(self):
        self.task_3.write({"stage_id": self.done_stage})
        self.task_3.refresh()
        self.assertEquals(self.done_stage, self.task_3.stage_id.id)
