from odoo.addons.project_milestone_status.tests.common import (
    ProjectMilestoneStatusCommon,
)


class TestProjectStatus(ProjectMilestoneStatusCommon):
    def test_check_execution_empty(self):
        self.assertEqual(self.project1._get_execution()["all_task"], 2)
        self.assertEqual(self.project1._get_execution()["executed_task"], 0)
        self.assertEqual(self.project1._get_execution()["executed"], 0)
        self.assertEqual(self.project1._get_execution()["percent"], 0)

    def test_check_execution_done(self):
        self.task1.write(
            {
                "stage_id": self.env["project.task.type"]
                .search([("fold", "=", True)], limit=1)
                .id
            }
        )
        self.assertEqual(self.project1._get_execution()["all_task"], 2)
        self.assertEqual(self.project1._get_execution()["executed_task"], 1)
        self.assertEqual(self.project1._get_execution()["executed"], 5)
        self.assertEqual(self.project1._get_execution()["percent"], 50)

        action = self.project1.action_view_executed_tasks()
        tasks = self.env["project.task"].search(action["domain"])
        self.assertEqual(tasks, self.task1)

        for button in self.project1._get_stat_buttons():
            if button["action"] == "action_view_executed_tasks":
                self.assertEqual(button["number"], "50% (5h)")
            elif button["action"] == "hr_timesheet.act_hr_timesheet_line_by_project":
                self.assertEqual(button["number"], "0% (0h)")

    def test_check_dedication_empty(self):
        self.assertEqual(self.project1._get_dedication()["dedicated"], 0)
        self.assertEqual(self.project1._get_dedication()["percent"], 0)

    def test_check_dedication_done(self):
        self.project1.milestone_ids.browse(self.milestone1.id)
        self.timesheet_line_model.create(
            {
                "name": "test",
                "employee_id": self.employee_1.id,
                "unit_amount": 2.0,
                "project_id": self.project1.id,
                "task_id": self.task1.id,
            }
        )
        self.assertEqual(self.project1._get_dedication()["dedicated"], 2)
        self.assertEqual(self.project1._get_dedication()["percent"], 20)

        for button in self.project1._get_stat_buttons():
            if button["action"] == "action_view_executed_tasks":
                self.assertEqual(button["number"], "0% (0h)")
            elif button["action"] == "hr_timesheet.act_hr_timesheet_line_by_project":
                self.assertEqual(button["number"], "20% (2h)")
