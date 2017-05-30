# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp Author Vincent Renaville
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def set_done(self):
        """ We will close related analytic account """
        self.mapped('analytic_account_id').write({'account_type': 'closed'})
        return super(ProjectProject, self).set_done()

    @api.multi
    def set_open(self):
        """ We will re-open related analytic account """
        self.mapped('analytic_account_id').write({'account_type': 'normal'})
        return super(ProjectProject, self).set_open()
