# -*- coding: utf-8 -*-
from odoo import models, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def toggle_active(self):
        for record in self:
            record.analytic_account_id.active = not record.active
        return super(ProjectProject, self).toggle_active()
