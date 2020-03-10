# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class Project(models.Model):
    _inherit = 'project.project'
    _parent_store = True

    parent_id = fields.Many2one(
       comodel_name='project.project', string='Parent Project'
    )
    child_ids = fields.One2many(comodel_name='project.project',
                                inverse_name='parent_id')
    parent_path = fields.Char(index=True)

    @api.multi
    def action_open_child_project(self):
        for rec in self:
            domain = [('parent_id', '=', rec.id)]
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'name': 'Children of %s' % rec.name,
                'view_mode': 'tree,form,graph',
                'res_model': 'project.project',
                'target': 'current',
                'domain': domain
            }
