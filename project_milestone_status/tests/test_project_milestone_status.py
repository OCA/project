from odoo.addons.project_milestone_status.tests.common import (
    ProjectMilestoneStatusCommon,
)


class TestProjectMilestoneStatus(ProjectMilestoneStatusCommon):
    def test_check_execution_empty(self):
        project_milestone_id = self.project1.milestone_ids.browse(self.milestone1.id)
        self.assertEqual(
            project_milestone_id.execution, 0, "There is no execution at the milestone"
        )

    def test_check_execution_done(self):
        project_milestone_id = self.project1.milestone_ids.browse(self.milestone1.id)
        self.task1.write(
            {
                "stage_id": self.env["project.task.type"]
                .search([("fold", "=", True)], limit=1)
                .id
            }
        )
        self.assertEqual(
            project_milestone_id.execution,
            50,
            "There is a 50 percent execution of the milestone",
        )

    def test_check_dedication_empty(self):
        project_milestone_id = self.project1.milestone_ids.browse(self.milestone1.id)
        self.assertEqual(
            project_milestone_id.dedication,
            0,
            "There is no dedication in the milestone",
        )

    def test_check_dedication_done(self):
        project_milestone_id = self.project1.milestone_ids.browse(self.milestone1.id)
        self.timesheet_line_model.create(
            {
                "name": "test",
                "employee_id": self.employee_1.id,
                "unit_amount": 2.0,
                "project_id": self.project1.id,
                "task_id": self.task1.id,
            }
        )
        self.assertEqual(
            project_milestone_id.dedication,
            20,
            "There is a 20 percent dedication in the milestone",
        )
