# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _


class BrGenerateProjects(models.TransientModel):
    _name = 'br.generate.projects'
    _description = 'Generate Projects'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        ondelete='set null',
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project to create the tasks',
        ondelete='set null',
        domain="[('partner_id', '!=', partner_id)]",
    )
    for_br = fields.Boolean('Create sub-projects for Business requirements')
    for_deliverable = fields.Boolean('Create sub-projects for Deliverables')

    @api.multi
    def wizard_view(self):
        view = self.env['ir.model.data'].get_object_reference(
            'business_requirement_project', 'view_br_generate_projects_form')

        action = {
            'name': _('Generate Projects'),
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
        project_ids = self.generate_projects()

        view = self.env['ir.model.data'].get_object_reference(
            'project', 'view_project')

        action = {
            # 'domain': "[('id','in',[%s])]" % ','.join(project_ids),
            'name': _('Projects'),
            'view_type': 'tree',
            'view_mode': 'list',
            'res_model': 'project.project',
            'view_id': view[1],
            'type': 'ir.actions.act_window'
        }
        return action

    @api.multi
    def generate_projects(self):
        project_obj = self.env['project.project']
        projects = []
        parent_project = self.project_id
        for br in parent_project.br_ids:
            if self.for_br:
                br_project_val = self._prepare_project_br(
                    br, parent_project.id)
                br_project = project_obj.create(br_project_val)
                projects.append(br_project.id)
                if not self.for_deliverable:
                    lines = [
                        line.resource_ids for line in br.deliverable_lines
                    ]
                    # self.create_project_task(lines, br_project.id)

            if self.for_deliverable:
                for line in br.deliverable_lines:
                    if self.for_br:
                        line_parent_id = br_project.id
                    else:
                        line_parent_id = parent_project.id
                    line_project_val = self._prepare_project_deliverable(
                        line, line_parent_id)
                    line_project = project_obj.create(line_project_val)
                    projects.append(line_project.id)

                    if not self.for_br:
                        lines = line.resource_ids
                        # self.create_project_task(lines, line_parent_id)

            if not self.for_br and not self.for_deliverable:
                lines = [line.resource_ids for line in br.deliverable_lines]
                # self.create_project_task(lines, parent_project.id)
                projects = [parent_project.id]
        return projects

    @api.multi
    def _prepare_project_br(self, br, parent_id):
        project = {
            'name': br.description,
            'parent_id': parent_id,
            'partner_id': br.partner_id.id,
        }
        return project

    @api.multi
    def _prepare_project_deliverable(self, line, parent_id):
        project = {
            'name': line.description,
            'parent_id': parent_id,
            'partner_id': line.business_requirement_id.partner_id.id,
        }
        return project

    @api.multi
    def _prepare_project_task(self, line, project_id):
        task = {
            # 'br_resource_id': line.br_resource_id.id,
            'name': line.task_name,
            'description': line.description,
            'sequence': line.sequence,
            'project_id': project_id,
            'planned_hours': line.qty,
        }
        return task

    @api.multi
    def create_project_task(self, lines, project_id):
        task_obj = self.env['project.task']
        for line in lines:
            task_val = self._prepare_project_task(
                line, project_id)
            task_obj.create(task_val)
