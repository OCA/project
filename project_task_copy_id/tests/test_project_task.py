# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.addons.base.tests.common import BaseCommon


class ProjectTask(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task = cls.env["project.task"].create({"name": "Test task"})

    def test_default_parameter(self):
        """Test default parameter."""
        self.env["ir.config_parameter"].sudo().search(
            [
                ("key", "=", "project_task_copy_id.prefix"),
            ]
        ).unlink()
        self.assertEqual(self.task.custom_task_ref, f"TASK-{self.task.id}")

    def test_parameter_change(self):
        """Test parameter change."""
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_copy_id.prefix", "TSK-"
        )
        self.assertEqual(self.task.custom_task_ref, f"TSK-{self.task.id}")
