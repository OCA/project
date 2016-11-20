# -*- coding: utf-8 -*-
# Copyright 2015 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.onchange('analytic_account_id')
    def onchange_analytic(self):
        res = super(ProjectTask, self).onchange_analytic()
        warn = self.analytic_account_id.project_task_warn
        if warn and warn != 'no-message':
            warn_msg = {
                'title': _("Warning: %s") % (self.name or ''),
                'message': self.analytic_account_id.project_task_warn_msg}
            if warn == 'block':
                self.analytic_account_id = None
                self.partner_id = None
                self.location_id = None
            res = {'warning': warn_msg}
        return res
