# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    sync_tasks_issues = fields.Boolean(
        string='Sync Issues and tasks',
        default=lambda x: x.use_issues and x.use_tasks
    )

    @api.depends('sync_tasks_issues')
    def sync_issues_for_tasks(self):
        if self.sync_tasks_issues:
            for task in self.task_ids:
                task.set_binded_issue_vals()
