# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    custom_task_ref = fields.Char(
        string="Custom Task Reference",
        help="Copy your custom Task Reference",
        compute="_compute_custom_task_ref",
        compute_sudo=True,
    )

    def _compute_custom_task_ref(self):
        """Compute custom task reference."""
        prefix = self.env["ir.config_parameter"].get_param(
            "project_task_copy_id.prefix",
            "TASK-",  # Default prefix if not set
        )
        for task in self:
            task.custom_task_ref = f"{prefix}{task.id}"
