# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestProjectMilestoneTimeKPI(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProjectMilestoneTimeKPI, cls).setUpClass()

        # create a generic Project with 2 milestones and 2 tasks associated to milestones
        cls.stage = cls.env["project.task.type"].create({
            "name": "New"
        })

        cls.project_a = cls.env["project.project"].create({
            "name": "Project A",
            "use_milestones": True,
        })

        cls.milestone_a = cls.env['project.milestone'].create({
            "name": "Analysis",
            "estimated_hours": 8,
            "project_id": cls.project_a.id,
        })
        cls.milestone_b = cls.env['project.milestone'].create({
            "name": "Realization",
            "estimated_hours": 20,
            "project_id": cls.project_a.id,
        })

        cls.task_a = cls.env["project.task"].create({
            "name": "Task A",
            "project_id": cls.project_a.id,
            "milestone_id": cls.milestone_a.id,
            "planned_hours": 4,
            "stage_id": cls.stage.id,
        })

        cls.task_b = cls.env["project.task"].create({
            "name": "Task B",
            "project_id": cls.project_a.id,
            "milestone_id": cls.milestone_b.id,
            "planned_hours": 8,
            "stage_id": cls.stage.id,
        })

        # Add timelines to created tasks
        cls.timesheet_a = cls.env["account.analytic.line"].create({
            "name": "Analyse",
            "project_id": cls.project_a.id,
            "task_id": cls.task_a.id,
            "unit_amount": 3,
            "employee_id": 1,
            "date": "2022-06-25",
        })

        cls.timesheet_b = cls.env["account.analytic.line"].create({
            "name": "Conception",
            "project_id": cls.project_a.id,
            "task_id": cls.task_b.id,
            "unit_amount": 4,
            "employee_id": 1,
            "date": "2022-06-30",
        })

    def test_timesheet_line_created(self):
        """ Test total_remaining_hours calculation after adding a new timeline to task """
        self.env["account.analytic.line"].create({
            "name": "Development",
            "project_id": self.project_a.id,
            "task_id": self.task_b.id,
            "unit_amount": 3,
            "employee_id": 1,
            "date": "2022-06-30",
        })
        assert self.project_a.total_estimated_hours == 28
        assert self.project_a.total_spent_hours == 10
        assert self.project_a.total_remaining_hours == 2

    def test_add_milestone(self):
        self.env['project.milestone'].create({
            "name": "Test",
            "estimated_hours": 8,
            "project_id": self.project_a.id,
        })
        assert self.project_a.total_estimated_hours == 36

    def test_unlink_milestone(self):
        self.milestone_b.unlink()
        assert self.project_a.total_estimated_hours == 8
        assert self.project_a.total_spent_hours == 3

    def test_update_milestone(self):
        self.milestone_a.write({"estimated_hours": 10})
        assert self.project_a.total_estimated_hours == 30
