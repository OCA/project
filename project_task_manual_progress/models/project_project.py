# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    manual_progress = fields.Float(
        compute="_compute_manual_progress",
        store=True,
        readonly=True,
        help="Shows the progress of the project based on the task manual progress",
    )

    @api.depends("task_ids.manual_progress")
    def _compute_manual_progress(self):
        for project in self:
            progress_tasks = project.task_ids
            if progress_tasks:
                project.manual_progress = (
                    sum(progress_tasks.mapped("manual_progress"))
                ) / len(progress_tasks)
            else:
                project.manual_progress = 0
