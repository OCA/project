# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Project(models.Model):
    _inherit = 'project.project'

    @api.multi
    def action_open_child_project(self):
        for rec in self:
            domain = [('parent_project_id', '=', rec.id)]
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form,graph',
                'res_model': 'project.project',
                'target': 'current',
                'domain': domain
            }
