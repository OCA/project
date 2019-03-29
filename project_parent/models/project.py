# © 2017-2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
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
