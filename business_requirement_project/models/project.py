# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.osv import osv


class Project(models.Model):
    _inherit = "project.project"

    origin = fields.Char('Source Document')

    @api.multi
    def generate_projects_wizard(self):
        br_ids = self.env.context.get('br_ids', False)
        from_project = False
        if not br_ids:
            br_ids = self.br_ids
            from_project = True
        default_uom = self.env['project.config.settings'].\
            get_default_time_unit('time_unit')
        default_uom = default_uom.get('time_unit', False)
        if not default_uom:
            raise osv.except_osv(
                _('Error!'),
                _("""Please set working time default unit in project config settings!
                """))
        lines = []
        for br in br_ids:
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
        if from_project:
            br_ids = [x for x in br_ids if x.parent_id.id is False]
        vals = {
            'partner_id': self.partner_id.id,
            'project_id': self.id,
            'br_ids': [(6, 0, [x.id for x in br_ids])]
        }
        wizard_obj = self.env['br.generate.projects']
        wizard = wizard_obj.with_context(
            default_uom=default_uom, br_ids=False).create(vals)
        action = wizard.wizard_view()
        return action


class ProjectTask(models.Model):
    _inherit = "project.task"

    br_resource_id = fields.Many2one(
        comodel_name='business.requirement.resource',
        string='Business Requirement Resource',
        ondelete='set null'
    )
