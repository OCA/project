# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class project_project(models.Model):
    _inherit = 'project.project'

    sync_tasks_issues = fields.Boolean(
       string='Sync Issues and tasks',
       default=lambda x: x.use_issues and x.use_tasks
    )

    @api.multi
    def sync_issues_for_tasks(self):
        """
        if we set a project with sync tasks_and_issues==true
        we will need to create issues for all tasks that have none
        and the tasks that already have an issue will be updated to sync
        from now on every time we modify a task  (user_id, stage) it will
        update the issue too (and viceversa)
        if we remove the syncing nothing happens.
        tasks and  issues will remain disconected.
        By triggering an empty write on every task, that will start update of
        all related issues and possible creation of missing issues.

        """
        if self.sync_tasks_issues:
            for task in self.task_ids:
                task.write({})

    def sync_all_projects(self):
        for project in self.env.filtered('sync_tasks_issues'):
            project.sync_issues_for_tasks()
