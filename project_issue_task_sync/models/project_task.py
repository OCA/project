# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sync_tasks_issues = fields.Boolean(
        related=['project_id', 'sync_tasks_issues']
    )
    issue_ids = fields.One2many('project.issue', 'task_id', 'Issues')

    def get_or_create_binded_issue(self):
        if self.issue_ids:
            return self.issue_ids[0]
        issue = self.env['project.issue'].with_context(
            mail_notrack=True, is_sync_operation=True).create({
                'project_id':  self.project_id.id,
                'name': self.name,
                'task_id':  self.id,
                'user_id': self.user_id.id,
                'stage_id': self.stage_id.id,
                'description': self.description or 'No Description'
                })
        return issue

    @api.multi
    def set_binded_issue_vals(self):
        for this in self:
            if not this.env.context.get('is_sync_operation'):
                if not this.issue_ids:
                    issue = this.get_or_create_binded_issue()
                for issue in this.issue_ids:
                    vals = self.env['project.issue'].get_changed_vals(
                        this, issue
                    )
                    issue.with_context(
                        mail_notrack=True, is_sync_operation=True
                    ).write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        this = super(ProjectTask, self).create(vals)
        if this.project_id.sync_tasks_issues:
            this.get_or_create_binded_issue()
        return this

    @api.multi
    def write(self, vals):
        blacklist = ['name', 'project_id']
        try:
            result = super(ProjectTask, self).write(vals=vals)
        except:
            only_wl_vals = {
                x: vals[x] for x in vals.keys() if x not in blacklist
            }
            result = super(ProjectTask, self).write(vals=only_wl_vals)
        for this in self:
            if this.project_id.sync_tasks_issues:
                this.set_binded_issue_vals()
        return result

    @api.multi
    def unlink(self):
        result = False
        for this in self:
            if this.project_id.sync_tasks_issues:
                if not self.env.context.get('is_sync_operation'):
                    # no sudo, we suppose that if you have decided to
                    # sync issues and tasks and you have delete privledges
                    # on one, you also have on the other.
                    this.with_context(
                        is_sync_operation=True).issue_ids.unlink()
            result = super(ProjectTask, this).unlink()
        return result
