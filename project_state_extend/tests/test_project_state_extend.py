# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import psycopg2

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProjectStateExtend(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProjectStateExtend = cls.env["project.state.extend"]
        cls.Project = cls.env["project.project"]

    def test_create_extend_state(self):
        """Test creating a custom state"""
        state = self.ProjectStateExtend.create(
            {
                "name": "Test State",
                "technical_name": "test_state",
                "color": 5,
                "sequence": 100,
            }
        )
        self.assertEqual(state.name, "Test State")
        self.assertEqual(state.technical_name, "test_state")
        self.assertEqual(state.color, 5)
        self.assertTrue(state.active)

    def test_unique_technical_name(self):
        """Test that technical_name must be unique"""
        # Clean up any existing test records
        existing = self.ProjectStateExtend.search(
            [("technical_name", "=", "unique_state_test_001")]
        )
        existing.unlink()

        # Create first state
        state1 = self.ProjectStateExtend.create(
            {
                "name": "State 1",
                "technical_name": "unique_state_test_001",
                "color": 1,
            }
        )
        self.assertTrue(state1.id)

        # Try to create duplicate - should raise IntegrityError
        with self.assertRaises(psycopg2.IntegrityError):
            with self.env.cr.savepoint():
                self.ProjectStateExtend.create(
                    {
                        "name": "State 2",
                        "technical_name": "unique_state_test_001",
                        "color": 2,
                    }
                )

        # Clean up test record
        state1.unlink()

    def test_project_custom_state_selection(self):
        """Test that custom states appear in project status selection"""
        # Create a custom state
        self.ProjectStateExtend.create(
            {
                "name": "Custom Project State",
                "technical_name": "custom_project_state",
                "color": 10,
            }
        )

        # Get extended status selection
        project = self.Project.create({"name": "Test Project"})
        selection = project._get_extended_status_selection()

        # Check that custom state is in selection
        technical_names = [s[0] for s in selection]
        self.assertIn("custom_project_state", technical_names)

        # Test assigning custom state
        project.last_update_status = "custom_project_state"
        self.assertEqual(project.last_update_status, "custom_project_state")

    def test_project_custom_state_color(self):
        """Test that custom state colors are computed correctly"""
        # Create custom state with specific color
        state = self.ProjectStateExtend.create(
            {
                "name": "Colored State",
                "technical_name": "colored_state_test",
                "color": 7,
            }
        )

        # Create project with custom state
        project = self.Project.create(
            {
                "name": "Test Project",
                "last_update_status": "colored_state_test",
            }
        )

        # Check that color is computed correctly
        self.assertEqual(project.last_update_color, 7)

        # Change state color and recompute
        state.color = 3
        project._compute_last_update_color()
        self.assertEqual(project.last_update_color, 3)

    def test_project_update_custom_state(self):
        """Test that custom states work in project updates"""
        # Create a custom state
        self.ProjectStateExtend.create(
            {
                "name": "Custom Update State",
                "technical_name": "custom_update_state",
                "color": 5,
            }
        )

        # Create project and project update
        project = self.Project.create({"name": "Test Project"})
        update = self.env["project.update"].create(
            {
                "project_id": project.id,
                "name": "Test Update",
                "status": "custom_update_state",
            }
        )

        # Check that custom state is assigned
        self.assertEqual(update.status, "custom_update_state")

        # Check that color is computed correctly
        self.assertEqual(update.color, 5)

    def test_native_states_preserved(self):
        """Test that native Odoo states are still available"""
        project = self.Project.create({"name": "Test Project"})
        selection = project._get_extended_status_selection()

        # Check that all native states are present
        native_states = ["on_track", "at_risk", "off_track", "on_hold", "to_define"]
        technical_names = [s[0] for s in selection]
        for native_state in native_states:
            self.assertIn(native_state, technical_names)

    def test_native_color_values(self):
        """Test native Odoo status colors are preserved."""
        project = self.Project.create(
            {"name": "Color Project", "last_update_status": "on_track"}
        )
        self.assertEqual(project.last_update_color, 20)
        project.last_update_status = "off_track"
        project._compute_last_update_color()
        self.assertEqual(project.last_update_color, 23)

        update = self.env["project.update"].create(
            {
                "project_id": project.id,
                "name": "Color Update",
                "status": "off_track",
            }
        )
        self.assertEqual(update.color, 23)

    def test_technical_name_format_validation(self):
        """Test technical name format validation."""
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.ProjectStateExtend.create(
                    {
                        "name": "Invalid State",
                        "technical_name": "Invalid State",
                        "color": 3,
                    }
                )

    def test_technical_name_native_collision(self):
        """Test technical name cannot match native status keys."""
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.ProjectStateExtend.create(
                    {
                        "name": "Native Collision",
                        "technical_name": "on_track",
                        "color": 3,
                    }
                )

    def test_cannot_delete_state_in_use(self):
        """Test state deletion is blocked while it is referenced."""
        state = self.ProjectStateExtend.create(
            {
                "name": "In Use State",
                "technical_name": "in_use_state_test",
                "color": 8,
            }
        )
        project = self.Project.create(
            {"name": "In Use Project", "last_update_status": state.technical_name}
        )
        self.assertTrue(project)

        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                state.unlink()

    def test_extend_state_archive(self):
        """Test archiving custom state"""
        state = self.ProjectStateExtend.create(
            {
                "name": "Archived State",
                "technical_name": "archived_state_test",
                "color": 1,
            }
        )
        self.assertTrue(state.active)

        state.active = False
        self.assertFalse(state.active)
