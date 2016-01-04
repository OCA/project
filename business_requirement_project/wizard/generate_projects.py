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
        parent_project = self.project_id
        for br in parent_project.br_ids:
            self.generate_projects(parent_project, br)

        view = self.env['ir.model.data'].get_object_reference(
            'project', 'view_project')

        action = {
            'domain': "[('partner_id','=',%s)]" % self.partner_id.id,
            'name': _('Projects'),
            'view_type': 'tree',
            'view_mode': 'list',
            'res_model': 'project.project',
            'view_id': view[1],
            'type': 'ir.actions.act_window'
        }
        return action

    def generate_projects(self, parent_project, br):
        project_obj = self.env['project.project']
        if self.for_br:
            br_project_val = self._prepare_project_br(
                br, parent_project.id)
            br_project = project_obj.create(br_project_val)
            if not self.for_deliverable:
                lines = [
                    line.resource_ids for line in br.deliverable_lines
                    if line.resource_ids
                ]
                self.create_project_task(lines, br_project.id)

        if self.for_deliverable:
            for line in br.deliverable_lines:
                if self.for_br:
                    line_parent_id = br_project.id
                else:
                    line_parent_id = parent_project.id
                line_project_val = self._prepare_project_deliverable(
                    line, line_parent_id)
                line_project = project_obj.create(line_project_val)
                self.create_project_task(line.resource_ids, line_project.id)

        if not self.for_br and not self.for_deliverable:
            lines = [
                line.resource_ids for line in br.deliverable_lines
                if line.resource_ids
            ]
            self.create_project_task(lines, parent_project.id)

        for child_br in br.business_requirement_ids:
            if child_br.project_id and \
                    (child_br.project_id.id == parent_project.id):
                continue
            self.generate_projects(parent_project, child_br)

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
        context = self.env.context
        default_uom = context and context.get('default_uom', False)
        product_uom_obj = self.env['product.uom']
        qty = product_uom_obj._compute_qty(
            line.uom_id.id, line.qty, default_uom)
        task = {
            'name': line.task_name,
            'description': line.description,
            'sequence': line.sequence,
            'project_id': project_id,
            'planned_hours': qty,
            'br_resource_id': line.id,
        }
        return task

    @api.multi
    def create_project_task(self, resource_lines, project_id):
        task_obj = self.env['project.task']
        for lines in resource_lines:
            for line in lines:
                task_val = self._prepare_project_task(
                    line, project_id)
                task_obj.create(task_val)
