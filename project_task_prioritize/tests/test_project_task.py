# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo.tests import common


class TestProjectTask(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProjectTask = self.env["project.task"]
        self.PrioritizerCategory = self.env["prioritizer.category"]
        self.PrioritizerCategoryLine = self.env["prioritizer.category.line"]
        self.ProjectProject = self.env["project.project"]

        # Create a project
        self.project = self.ProjectProject.create({"name": "Test Project"})

        # Create prioritizer categories
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

        self.category2 = self.PrioritizerCategory.create(
            {
                "name": "Urgency",
                "prioritizer_category_line_ids": [
                    (0, 0, {"name": "Low", "value": 1}),
                    (0, 0, {"name": "High", "value": 5}),
                ],
            }
        )

        # Add categories to project
        self.project.write(
            {
                "prioritizer_category_ids": [
                    (6, 0, [self.category1.id, self.category2.id])
                ]
            }
        )

    def test_01_task_prioritizer_value(self):
        """Test computation of prioritizer_value"""
        # Create a task
        task = self.ProjectTask.create(
            {
                "name": "Test Task",
                "project_id": self.project.id,
                "allocated_hours": 10,
            }
        )

        # Get category lines
        importance_high = self.category1.prioritizer_category_line_ids.filtered(
            lambda x: x.name == "High"
        )
        urgency_high = self.category2.prioritizer_category_line_ids.filtered(
            lambda x: x.name == "High"
        )

        # Assign prioritizer lines to task
        task.write(
            {"prioritizer_line_ids": [(6, 0, (importance_high + urgency_high).ids)]}
        )

        # Test with default formula
        expected_value = (3 + 5) / (10 * (3 + 5 - (3 + 5) + 1))  # Default formula
        self.assertEqual(task.prioritizer_value, expected_value)

    def test_02_custom_prioritizer_formula(self):
        """Test custom prioritizer formula"""
        # Set a custom formula
        custom_formula = "prioritizer_sum / allocated_hours"
        self.project.write({"prioritizer_formula": custom_formula})

        # Create a task
        task = self.ProjectTask.create(
            {
                "name": "Custom Formula Task",
                "project_id": self.project.id,
                "allocated_hours": 4,
            }
        )

        # Assign prioritizer lines (High importance = 3, High urgency = 5)
        importance_high = self.category1.prioritizer_category_line_ids.filtered(
            lambda x: x.name == "High"
        )
        urgency_high = self.category2.prioritizer_category_line_ids.filtered(
            lambda x: x.name == "High"
        )
        task.write(
            {"prioritizer_line_ids": [(6, 0, (importance_high + urgency_high).ids)]}
        )

        # Test with custom formula (3 + 5) / 4 = 2.0
        self.assertEqual(task.prioritizer_value, 2.0)

    def test_03_invalid_formula(self):
        """Test behavior with invalid formula"""
        # Set an invalid formula
        self.project.write(
            {"prioritizer_formula": "1 / 0"}
        )  # Will cause division by zero

        # Create a task
        task = self.ProjectTask.create(
            {
                "name": "Invalid Formula Task",
                "project_id": self.project.id,
                "allocated_hours": 10,
            }
        )

        # Assign prioritizer lines
        importance_high = self.category1.prioritizer_category_line_ids.filtered(
            lambda x: x.name == "High"
        )
        task.write({"prioritizer_line_ids": [(6, 0, importance_high.ids)]})

        # Should default to 0 on error
        self.assertEqual(task.prioritizer_value, 0)

    def test_04_using_today_value(self):
        """Test custom prioritizer formula"""
        # Set a custom formula
        custom_formula = "(rec.date_deadline - today).days / allocated_hours"
        self.project.write({"prioritizer_formula": custom_formula})

        # Create a task
        task = self.ProjectTask.create(
            {
                "name": "Custom Formula Task",
                "project_id": self.project.id,
                "allocated_hours": 4,
                "date_deadline": datetime.datetime.today() + datetime.timedelta(days=8),
            }
        )

        # Assign prioritizer lines (High importance = 3, High urgency = 5)
        importance_high = self.category1.prioritizer_category_line_ids.filtered(
            lambda x: x.name == "High"
        )
        urgency_high = self.category2.prioritizer_category_line_ids.filtered(
            lambda x: x.name == "High"
        )
        task.write(
            {"prioritizer_line_ids": [(6, 0, (importance_high + urgency_high).ids)]}
        )

        # Test with custom formula 7 / 4 = 1.75
        self.assertEqual(task.prioritizer_value, 1.75)
