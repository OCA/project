# -*- coding: utf-8 -*-
# © 2015
# Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api
from openerp.tools.translate import _


class BrGenerateProject(models.TransientModel):
    _name = 'br.generate.project'
    _description = 'Generate Project'

    name = fields.Char('Project Name')
    br_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Business Requirement',
        ondelete='set null'
    )

    @api.multi
    def wizard_view(self):
        view = self.env['ir.model.data'].get_object_reference(
            'business_requirement_project', 'view_br_generate_project_form')

        action = {
            'name': _('Generate Project'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'views': [(view[1], 'form')],
            'view_id': view[1],
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }
        return action

    @api.multi
    def apply(self):
        project = self.generate_project()
        project_id = project.id
        self.br_id.update_project_id(project_id)

        view = self.env['ir.model.data'].get_object_reference(
            'project', 'edit_project')
        action = {
            'name': _('Project'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.project',
            'view_id': view[1],
            'type': 'ir.actions.act_window',
            'res_id': project_id or False,
        }
        return action

    @api.multi
    def generate_project(self):
        project_obj = self.env['project.project']
        vals = {
            'name': self.name,
        }
        return project_obj.create(vals)
