# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPrioritizerCategory(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.PrioritizerCategory = self.env["prioritizer.category"]
        self.PrioritizerCategoryLine = self.env["prioritizer.category.line"]

    def test_01_create_prioritizer_category(self):
        """Test creation of a prioritizer category with lines"""
        # Create a prioritizer category with lines
        category = self.PrioritizerCategory.create(
            {
                "name": "Test Category",
                "prioritizer_category_line_ids": [
                    (0, 0, {"name": "Low", "value": 1}),
                    (0, 0, {"name": "Medium", "value": 2}),
                    (0, 0, {"name": "High", "value": 3}),
                ],
            }
        )
        self.assertEqual(len(category.prioritizer_category_line_ids), 3)
        self.assertEqual(category.max_value, 3)

    def test_02_compute_max_value(self):
        """Test computation of max_value field"""
        # Create a prioritizer category with lines
        category = self.PrioritizerCategory.create(
            {
                "name": "Test Category",
                "prioritizer_category_line_ids": [
                    (0, 0, {"name": "Low", "value": 5}),
                    (0, 0, {"name": "High", "value": 10}),
                ],
            }
        )
        self.assertEqual(category.max_value, 10)

        # Add a new line with a higher value
        self.PrioritizerCategoryLine.create(
            {
                "name": "Critical",
                "value": 15,
                "prioritizer_category_id": category.id,
            }
        )
        self.assertEqual(category.max_value, 15)

    def test_03_empty_category(self):
        """Test behavior with empty category"""
        category = self.PrioritizerCategory.create({"name": "Empty Category"})
        self.assertEqual(category.max_value, 1)  # Default value when no lines exist
