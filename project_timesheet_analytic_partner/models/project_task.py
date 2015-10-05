# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if vals.get('partner_id') is not None:
            # Change the other partner of all tasks works timesheet entries
            self.mapped('work_ids.hr_analytic_timesheet_id').write(
                {'other_partner_id': vals['partner_id']})
        return res
