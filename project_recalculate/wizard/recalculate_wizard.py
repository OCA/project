# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _


class ProjectRecalculateWizard(models.TransientModel):
    _name = 'project.recalculate.wizard'

    project_id = fields.Many2one(
        comodel_name='project.project', readonly=True, string="Project")
    calculation_type = fields.Selection(
        string='Calculation type', related='project_id.calculation_type',
        readonly=True)
    project_date = fields.Date(readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super(ProjectRecalculateWizard, self).default_get(fields_list)
        res['project_id'] = self.env.context.get('active_id', False)
        project = self.env['project.project'].browse(res['project_id'])
        if not project.calculation_type:
            raise Warning(_('Cannot recalculate project because your project '
                            'don\'t have calculation type.'))
        if project.calculation_type == 'date_begin' and not project.date_start:
            raise Warning(_('Cannot recalculate project because your project '
                            'don\'t have date start.'))
        if project.calculation_type == 'date_end' and not project.date:
            raise Warning(_('Cannot recalculate project because your project '
                            'don\'t have date end.'))
        res['project_date'] = (project.date_start
                               if project.calculation_type == 'date_begin'
                               else project.date)
        return res

    @api.one
    def confirm_button(self):
        return self.project_id.project_recalculate()
