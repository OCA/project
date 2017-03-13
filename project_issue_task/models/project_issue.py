# -*- coding: utf-8 -*-
# © 2012 - 2013 Daniel Reis
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import  api, models, _


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    def action_create_task(self):
        values = {
                      'name': _('Report for %s') % self.name,
                      'issue_id': self.id,
                      'tag_ids': [(6, False, self.tag_ids.mapped('id'))]
                  }
        fields = ['project_id']    # For optional relational fields
        values.update((field, getattr(self, field).id) for field in fields
                            if hasattr(self, field) and getattr(self, field))
        rec_task = self.env['project.task']
        task_id = rec_task.create(values)
        self.task_id = task_id
        res = {
            'name': _('Issue Task Report'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'res_id': task_id.id,
            'type': 'ir.actions.act_window'}
        return res

    @api.multi
    def toggle_active(self):
        """ On Issue Close, also Close Task """
        rec_tasks = self.mapped('task_id')
        rec_tasks.write({'active': not self.active})
        return super(ProjectIssue, self).toggle_active()
