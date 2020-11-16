# -*- coding: utf-8 -*-
# (c) 2015 Incaser Informatica S.L. - Sergio Teruel
# (c) 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    case_default = fields.Boolean(
        string='Default for New Projects',
        help='If you check this field, this stage will be proposed by default '
             'on each new project. It will not assign this stage to existing '
             'projects.')


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _get_type_common(self):
        ids = self.env['project.task.type'].search([
            ('case_default', '=', True)])
        return ids

    type_ids = fields.Many2many(
        comodel_name='project.task.type', relation='project_task_type_rel',
        column1='project_id', column2='type_id', string='Tasks Stages',
        states={
            'close': [('readonly', True)],
            'cancelled': [('readonly', True)]
        }, default=_get_type_common
    )
