# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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
        domain="[('partner_id', '=', partner_id)]",
    )
    for_br = fields.Boolean('Create sub-projects for Business requirements')
    for_deliverable = fields.Boolean('Create sub-projects for Deliverables')
    for_childs = fields.Boolean(
        'Create sub-projects for Child Business requirements')
    br_ids = fields.Many2many(
        string='Business requirements',
        comodel_name='business.requirement',
        relation='wizard_br_rel',
        column1='wizard_id',
        column2='br_id'
    )

    @api.onchange('for_br')
    def _onchange_for_br(self):
        if not self.for_br:
            self.for_childs = False

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
        task_ids = []
        project_ids = []
        parent_project = self.project_id
        if not self.for_br and not self.for_deliverable:
            for br in self.br_ids:
                lines = [
                    line.resource_ids for line in br.deliverable_lines
                    if line.resource_ids
                ]
                self.create_project_task(lines, parent_project.id, task_ids)
        else:
            for br in self.br_ids:
                self.generate_br_projects(
                    parent_project, br, project_ids, task_ids)
        if project_ids:
            ids = ['%s' % x for x in project_ids]
            res_model = 'project.project'
            name = 'Project'
        else:
            ids = ['%s' % x for x in task_ids]
            res_model = 'project.task'
            name = 'Task'
        action = {
            'domain': "[('id','in',[%s])]" % ','.join(ids),
            'name': _(name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': res_model,
            'type': 'ir.actions.act_window'
        }
        return action

    def has_generated(self, br):
        origin = '%s.%s' % (br._name, br.id)
        project_obj = self.env['project.project']
        project = project_obj.search([('origin', '=', origin)])
        return project

    @api.multi
    def generate_br_projects(self, parent_project, br, project_ids, task_ids):
        project_obj = self.env['project.project']
        br_project = False
        if self.for_br:
            br_project = self.has_generated(br)
            if br_project:
                br_project = br_project[0]
            elif not br.linked_project:
                br_project_val = self._prepare_project_vals(
                    br, parent_project)
                br_project = project_obj.create(br_project_val)
                br.linked_project = br_project.id
                project_ids.append(br_project.id)
            else:
                br_project = br.linked_project
                project_ids.append(br_project.id)
            if not self.for_deliverable:
                lines = [
                    line.resource_ids for line in br.deliverable_lines
                    if line.resource_ids
                ]
                self.create_project_task(lines, br_project.id, task_ids)

        if self.for_deliverable:
            if self.for_br:
                line_parent = br_project
            else:
                line_parent = parent_project
            self.generate_deliverable_projects(
                line_parent, br.deliverable_lines, project_ids, task_ids)

        if self.for_childs:
            br_project = br_project or parent_project
            for child_br in br.business_requirement_ids:
                self.generate_br_projects(
                    br_project, child_br, project_ids, task_ids)

    @api.multi
    def generate_deliverable_projects(
            self, parent_project, deliverable_lines, project_ids, task_ids):
        project_obj = self.env['project.project']
        for line in deliverable_lines:
            line_project = self.has_generated(line)
            if line_project:
                line_project = line_project[0]
            else:
                line_project_val = self._prepare_project_vals(
                    line, parent_project)
                line_project = project_obj.create(line_project_val)
                line.linked_project = line_project.id
                project_ids.append(line_project.id)
            self.create_project_task(
                line.resource_ids, line_project.id, task_ids)

    @api.multi
    def _prepare_project_vals(self, br, parent):
        vals = {
            'name': br.description,
            'parent_id': parent.analytic_account_id.id,
            'partner_id': parent.partner_id.id,
            'members': [(6, 0, [x.id for x in parent.members])],
            'message_follower_ids': [
                x.id for x in parent.message_follower_ids],
            'user_id': parent.user_id.id,
            'origin': '%s.%s' % (br._name, br.id),
            'privacy_visibility': '%s' % (br.project_id.privacy_visibility)
        }
        return vals

    @api.multi
    def _prepare_project_task(self, line, project_id):
        context = self.env.context
        default_uom = context and context.get('default_uom', False)
        product_uom_obj = self.env['product.uom']
        qty = product_uom_obj._compute_qty(
            line.uom_id.id, line.qty, default_uom)
        name = line.description
        br_id = False
        if self.for_br:
            name = line.business_requirement_deliverable_id\
                .business_requirement_id.name + '-' + name
            br_id = line.business_requirement_deliverable_id\
                .business_requirement_id.id
        vals = {
            'name': name,
            'description': line.description,
            'sequence': line.sequence,
            'project_id': project_id,
            'planned_hours': qty,
            'remaining_hours': qty,
            'br_resource_id': line.id,
            'user_id': line.user_id.id,
            'task_categ_id': line.task_categ_id.id,
            'business_requirement_id': br_id,
        }
        return vals

    @api.multi
    def create_project_task(self, resource_lines, project_id, task_ids=[]):
        task_obj = self.env['project.task']
        for lines in resource_lines:
            for line in lines:
                if line.resource_type != 'task':
                    continue
                generated = self.env['project.task'].search(
                    [('br_resource_id', '=', line.id)])
                if generated:
                    continue
                task_val = self._prepare_project_task(
                    line, project_id)
                task = task_obj.create(task_val)
                task_ids.append(task.id)
