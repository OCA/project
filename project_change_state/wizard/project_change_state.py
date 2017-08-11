# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class ProjectChangeState(models.TransientModel):
    _name = "project.change.state"
    _description = "Change the status of the selected projects"

    @api.multi
    def set_pending(self):
        project_ids = self.env.context.get('active_ids')
        projects = self.env['project.project'].browse(project_ids)
        projects.set_pending()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def set_open(self):
        project_ids = self.env.context.get('active_ids')
        projects = self.env['project.project'].browse(project_ids)
        projects.set_open()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def set_done(self):
        project_ids = self.env.context.get('active_ids')
        projects = self.env['project.project'].browse(project_ids)
        projects.set_done()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def set_cancel(self):
        project_ids = self.env.context.get('active_ids')
        projects = self.env['project.project'].browse(project_ids)
        projects.set_cancel()
        return {'type': 'ir.actions.act_window_close'}
