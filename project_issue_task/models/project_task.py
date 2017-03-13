# -*- coding: utf-8 -*-
# © 2012 - 2013 Daniel Reis
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class Task(models.Model):
    _inherit = "project.task"

    issue_id = fields.Many2one('project.issue', string='Issue', store=True,
                               compute='_compute_issue')
    ref = fields.Char(string='Reference')
    reason_id = fields.Many2one('project.task.cause', string='Problem Cause')

    @api.multi
    def _compute_issue(self):
        rec_issue = self.env['project.issue']
        for task in self:
            args = [('task_id', '=', task.id)]
            task.issue_id = rec_issue.search(args, limit=1)

    @api.multi
    def toggle_active(self):
        """ On Task Close, also close Issue """
        rec_issues = self.mapped('issue_id')
        rec_issues.write({'active': not self.active})
        return super(Task, self).toggle_active()
