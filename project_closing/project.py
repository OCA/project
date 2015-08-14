# -*- coding: utf-8 -*-
from openerp import api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def set_done(self):
        """ We will close related analytic account """
        self.mapped('analytic_account_id').write({'state': 'close'})
        return super(ProjectProject, self).set_done()

    @api.multi
    def set_open(self):
        """ We will re-open related analytic account """
        self.mapped('analytic_account_id').write({'state': 'open'})
        return super(ProjectProject, self).set_open()
