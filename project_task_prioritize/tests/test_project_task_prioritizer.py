# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProjectTaskPrioritizer(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProjectTask = self.env["project.task"]
        self.PrioritizerCategory = self.env["prioritizer.category"]
        self.PrioritizerCategoryLine = self.env["prioritizer.category.line"]
        self.ProjectProject = self.env["project.project"]
        self.ProjectTaskPrioritizer = self.env["project.task.prioritizer"]

        # Create a project
        self.project = self.ProjectProject.create({"name": "Test Project"})

        # Create prioritizer categories with lines
        self.category1 = self.PrioritizerCategory.create(
            {
                "name": "Importance",
                "prioritizer_category_line_ids": [
                    (0, 0, {"name": "Low", "value": 1}),
                    (0, 0, {"name": "Medium", "value": 2}),
                    (0, 0, {"name": "High", "value": 3}),
                ],
            }
        )

        # Add categories to project
        self.project.write({"prioritizer_category_ids": [(6, 0, [self.category1.id])]})

        # Create tasks
        self.task1 = self.ProjectTask.create(
            {
                "name": "Task 1",
                "project_id": self.project.id,
            }
        )
        self.task2 = self.ProjectTask.create(
            {
                "name": "Task 2",
                "project_id": self.project.id,
            }
        )

    def test_prioritizer_wizard_default_get(self):
        """Test default_get method of the wizard"""
        # Create wizard with task context
        wizard = self.ProjectTaskPrioritizer.with_context(
            active_model="project.task", active_ids=[self.task1.id, self.task2.id]
        ).create({})

        # Should have 2 tasks and 2 lines (one for each task-category combination)
        self.assertEqual(len(wizard.task_ids), 2)
        self.assertEqual(len(wizard.line_ids), 2)  # 2 tasks * 1 category each
        self.assertIn(self.task1, wizard.task_ids)
        self.assertIn(self.task2, wizard.task_ids)

    def test_prioritizer_wizard_validate(self):
        """Test button_validate method of the wizard"""
        # Get category lines
        importance_high = self.category1.prioritizer_category_line_ids.filtered(
            lambda x: x.name == "High"
        )
        importance_medium = self.category1.prioritizer_category_line_ids.filtered(
            lambda x: x.name == "Medium"
        )

        # Create wizard with task context
        wizard = self.ProjectTaskPrioritizer.with_context(
            active_model="project.task", active_ids=[self.task1.id, self.task2.id]
        ).create({})

        # Update lines with priorities
        for line in wizard.line_ids:
            if line.task_id == self.task1:
                line.prioritizer_category_line_id = importance_high
            else:
                line.prioritizer_category_line_id = importance_medium

        # Validate the wizard
        wizard.button_validate()

        # Check that tasks have the correct prioritizer lines
        self.assertEqual(self.task1.prioritizer_line_ids, importance_high)
        self.assertEqual(self.task2.prioritizer_line_ids, importance_medium)

    def test_prioritizer_wizard_no_tasks(self):
        """Test wizard with no tasks in context"""
        # Create wizard with no task context
        wizard = self.ProjectTaskPrioritizer.with_context(
            active_model="project.task", active_ids=[]
        ).create({})

        # Should have no tasks or lines
        self.assertEqual(len(wizard.task_ids), 0)
        self.assertEqual(len(wizard.line_ids), 0)

    def test_prioritizer_wizard_wrong_model(self):
        """Test wizard with wrong model in context"""
        # Should raise assertion for wrong model
        with self.assertRaises(AssertionError):
            self.ProjectTaskPrioritizer.with_context(
                active_model="wrong.model", active_ids=[1, 2, 3]
            ).create({})

    def test_prioritizer_wizard_line_creation(self):
        """Test _get_matrix_lines method"""
        # Create a second category
        category2 = self.PrioritizerCategory.create(
            {
                "name": "Urgency",
                "prioritizer_category_line_ids": [
                    (0, 0, {"name": "Low", "value": 1}),
                    (0, 0, {"name": "High", "value": 3}),
                ],
            }
        )

        # Add second category to project
        self.project.write({"prioritizer_category_ids": [(4, category2.id)]})

        # Create wizard with task context
        wizard = self.ProjectTaskPrioritizer.with_context(
            active_model="project.task", active_ids=[self.task1.id]
        ).create({})

        # Should have 2 lines (one for each category)
        self.assertEqual(len(wizard.line_ids), 2)
        categories = wizard.line_ids.mapped("prioritizer_category_id")
        self.assertIn(self.category1, categories)
        self.assertIn(category2, categories)
