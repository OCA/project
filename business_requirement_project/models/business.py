# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.osv import osv


class Project(models.Model):
    _inherit = "project.project"

    @api.multi
    def generate_tasks_wizard(self):
        lines = []
        for br in self.br_ids:
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
                    line = (
                        0, 0,
                        {
                            'br_id': br.id,
                            'br_resource_id': line.id,
                            'name': line.description,
                            'sequence': line.sequence,
                            'resource_time_total': line.resource_time,
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
