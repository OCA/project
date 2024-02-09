# Copyright 2014 Daniel Reis
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProjectTaskType(models.Model):
    """Added state in the Project Task Type."""

    _inherit = "project.task.type"

    @api.model
    def _get_task_states(self):
        return [
            ("draft", "New"),
            ("open", "In Progress"),
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ]

    state = fields.Selection(selection="_get_task_states")
