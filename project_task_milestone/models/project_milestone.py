# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    project_task_ids = fields.One2many(
        "project.task", "milestone_id", string="Project Tasks"
    )
