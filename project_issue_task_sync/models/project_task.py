# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    issue_ids = fields.One2many('project.issue', 'task_id', 'Issues')

    # CAN EXTEND THIS TO SYNC MORE FILES, if we want to create a model
    # fields to sync we can do it here.


    def get_changed_vals(self):
        vals = {}
        if self.issue_ids[:1].stage_id != self.stage_id:
            vals['stage_id'] = self.stage_id.id
        if self.issue_ids[:1].user_id != self.user_id:
            vals['user_id'] = self.user_id.id
        return vals

    @api.multi
    def set_issue_vals(self):
        for this in self:
            # If I see that on write or create my task has no issue , create
            # it obviously as a sync_operation / no mail
            if not len(this.issue_ids) > 0:
               self.env['project.issue'].with_context(
                   mail_notrack=True, is_sync_operation=True).create(
                   { 
                     'project_id':  self.project_id.id,
                     'name': self.name,
                     'task_id':  self.id,
                     'user_id': self.user_id.id,
                     'stage_id': self.stage_id.id,
                     'description': self.description
                   }
                )
            if (this.project_id.sync_tasks_issues and not
                    self.env.context.get('is_sync_operation')):
                vals = this.get_changed_vals()
                # NOTE we will write on all issues if they are multiple
                if vals:
                   this.issue_ids.with_context(
                       mail_notrack=True, sync_operation=True
                   ).write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        this = super(ProjectTask, self).create(vals)
        this.set_issue_vals()
        return this

    @api.multi
    def write(self, vals):
      result = super(ProjectTask, self).write(vals)
      self.set_issue_vals()
      return result
