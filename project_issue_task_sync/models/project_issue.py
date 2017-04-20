# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    def get_changed_vals(self, task):
        vals = {}
        if task.stage_id != self.stage_id:
            vals['stage_id'] = self.stage_id.id
        if task.user_id != self.user_id:
            vals['user_id'] = self.user_id.id
        return vals

    def set_issue_vals(self):
        for this in self:
            task = this.sudo().task_id[:1]
            # TODO task creation? for now if there is no task just skip.
            if (this.project_id.sync_tasks_issues and task and not
                    self.env.context.get('is_sync_operation')):
                vals = this.get_changed_vals(task)
                if vals:
                    this.task.with_context(
                        mail_notrack=True, is_sync_operation=True
                    ).write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        this = super(ProjectIssue, self).create(vals)
        this.set_issue_vals()
        return this

    @api.multi
    def write(self, vals):
        result = super(ProjectIssue, self).write(vals)
        self.set_issue_vals()
        return result
