# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models, fields


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    sync_tasks_issues = fields.Boolean(
        related=['project_id', 'sync_tasks_issues']
    )

    def get_changed_vals(self, origin, paired):
        vals = {}
        if paired.stage_id != origin.stage_id:
            vals['stage_id'] = origin.stage_id.id
        if paired.user_id != origin.user_id:
            vals['user_id'] = origin.user_id.id
        if paired.name != origin.name:
            vals['name'] = origin.name
        if paired.description != origin.description:
            vals['description'] = origin.description
        if paired.project_id != origin.project_id:
            vals['project_id'] = origin.project_id.id
        return vals

    def get_or_create_binded_task(self):
        if self.task_id:
            return self.task_id
        task = self.env['project.task'].with_context(
            mail_notrack=True, is_sync_operation=True).create({
                'project_id':  self.project_id.id,
                'name': self.name,
                'issue_ids': [(4, self.id)],
                'user_id': self.user_id.id,
                'stage_id': self.stage_id.id,
                'description': self.description or 'No Description'
            })
        return task

    def set_binded_task_vals(self):
        for this in self:
            if not this.env.context.get('is_sync_operation'):
                task = this.task_id
                if not len(task) > 0:
                    task = this.get_or_create_binded_task()
                vals = this.get_changed_vals(this, task)
                task.with_context(
                    mail_notrack=True, is_sync_operation=True
                ).write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        this = super(ProjectIssue, self).create(vals)
        if this.project_id.sync_tasks_issues:
            this.get_or_create_binded_task()
        return this

    @api.multi
    def write(self, vals):
        result = super(ProjectIssue, self).write(vals)
        if self.project_id.sync_tasks_issues:
            self.set_binded_task_vals()
        return result

    @api.multi
    def unlink(self):
        result = False
        for this in self:
            if this.project_id.sync_tasks_issues:
                if not self.env.context.get('is_sync_operation'):
                    # no sudo, we suppose that if you have decided to sync
                    # issues and tasks and you have delete privledges on one,
                    # you also have on the other.
                    this.with_context(is_sync_operation=True).task_id.unlink()
            result = super(ProjectIssue, this).unlink()
        return result
