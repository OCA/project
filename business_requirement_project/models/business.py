# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.osv import osv


class Project(models.Model):
    _inherit = "project.project"

    @api.multi
    def generate_projects_wizard(self):
        default_uom = self.env['project.config.settings'].\
            get_default_time_unit('time_unit')
        default_uom = default_uom.get('time_unit', False)
        if not default_uom:
            raise osv.except_osv(
                _('Error!'),
                _("""Please set working time default unit in project config settings!
                """))
        lines = []
        for br in self.br_ids:
            if br.state not in ['approved', 'cancel', 'done']:
                raise osv.except_osv(
                    _('Error!'),
                    _("""All business requirement of the project should be approved/canceled/done!
                    """))
            if br.state != 'approved':
                continue
            for deliverables in br.deliverable_lines:
                for line in deliverables.resource_ids:
                    if line.resource_type != 'task':
                        continue
                    generated = self.env['project.task'].search(
                        [('br_resource_id', '=', line.id)])
                    if generated:
                        continue
                    lines.append(line.id)

        if not lines:
            raise osv.except_osv(
                _('Error!'),
                _("""There is no available business requirement resource line to
                    generate task!"""))

        vals = {
            'partner_id': self.partner_id.id,
            'project_id': self.id,
        }
        wizard_obj = self.env['br.generate.projects']
        wizard = wizard_obj.with_context(default_uom=default_uom).create(vals)
        action = wizard.wizard_view()
        return action

    @api.multi
    def generate_tasks_wizard(self):
        product_uom_obj = self.env['product.uom']
        default_uom = self.env['project.config.settings'].\
            get_default_time_unit('time_unit')
        default_uom = default_uom.get('time_unit', False)
        if not default_uom:
            raise osv.except_osv(
                _('Error!'),
                _("""Please set working time default unit in project config settings!
                """))
        lines = []
        for br in self.br_ids:
            if br.state not in ['approved', 'cancel', 'done']:
                raise osv.except_osv(
                    _('Error!'),
                    _("""All business requirement of the project should be approved/canceled/done!
                    """))
            if br.state != 'approved':
                continue
            for deliverables in br.deliverable_lines:
                for line in deliverables.resource_ids:
                    if line.resource_type != 'task':
                        continue
                    generated = self.env['project.task'].search(
                        [('br_resource_id', '=', line.id)])
                    if generated:
                        continue
                    qty = product_uom_obj._compute_qty(
                        line.uom_id.id, line.qty, default_uom)
                    line = (
                        0, 0,
                        {
                            'br_id': br.id,
                            'br_resource_id': line.id,
                            'name': line.task_name,
                            'description': line.description,
                            'sequence': line.sequence,
                            'resource_time_total': qty,
                            'uom_id': default_uom,
                            'user_id': line.user_id.id,
                            'select': True,
                        }
                    )
                    lines.append(line)

        if not lines:
            raise osv.except_osv(
                _('Error!'),
                _("""There is no available business requirement resource line to
                    generate task!"""))

        vals = {
            'project_id': self.id,
            'lines': lines,
        }
        wizard_obj = self.env['br.generate.tasks']
        wizard = wizard_obj.create(vals)
        action = wizard.wizard_view()
        return action


class ProjectTask(models.Model):
    _inherit = "project.task"

    br_resource_id = fields.Many2one(
        comodel_name='business.requirement.resource',
        string='Business Requirement Resource',
        ondelete='set null'
    )
