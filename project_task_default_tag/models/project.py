# Copyright 2018 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    tag_ids = fields.Many2many(
        comodel_name='project.tags',
        string='Tags')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def default_get(self, fields):
        res = super(ProjectTask, self).default_get(fields)
        project_id = res.get('project_id')
        if project_id:
            project = self.env['project.project'].browse(project_id)
            res.update({
                'tag_ids': [(6, 0, project.tag_ids.ids)],
            })
        return res

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.tag_ids = self.project_id.tag_ids
