from odoo.tests.common import TransactionCase

# Import the uninstall_hook function
from ..hooks import uninstall_hook


class TestUninstallHook(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create some sample tasks with different priorities

        self.task_normal = self.env["project.task"].create(
            {
                "name": "Task with Normal Priority",
                "priority": "1",  # Normal priority
            }
        )
        self.task_high = self.env["project.task"].create(
            {
                "name": "Task with High Priority",
                "priority": "2",  # High priority
            }
        )
        self.task_very_high = self.env["project.task"].create(
            {
                "name": "Task with Very High Priority",
                "priority": "3",  # Very High priority
            }
        )

    def test_uninstall_hook(self):
        """
        Test that the uninstall_hook correctly updates the priority
        of tasks with 'High' and 'Very High' priorities to 'Normal'.
        """

        # Call the uninstall hook
        uninstall_hook(self.env)

        # Assert that the priorities have been updated correctly
        self.assertEqual(
            self.task_high.priority,
            "1",
            "High priority task should be updated to Normal.",
        )
        self.assertEqual(
            self.task_very_high.priority,
            "1",
            "Very High priority task should be updated to Normal.",
        )
        self.assertEqual(
            self.task_normal.priority,
            "1",
            "Normal priority task should remain unchanged.",
        )
