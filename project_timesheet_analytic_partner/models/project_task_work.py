# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class ProjectTaskWork(models.Model):
    _inherit = 'project.task.work'

    @api.model
    def create(self, vals):
        task_work = super(ProjectTaskWork, self).create(vals)
        if task_work.task_id.partner_id:
            task_work.hr_analytic_timesheet_id.other_partner_id = (
                task_work.task_id.partner_id)
        return task_work
