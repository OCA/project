# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2014 Antiun Ingenieria S.L. (Madrid, Spain, http://www.antiun.com)
#                 Endika Iglesias <endikaig@antiun.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.exceptions import Warning  # , RedirectWarning
from openerp.tools.translate import _


class ProjectRecalculateWizard(models.TransientModel):
    _name = 'project.recalculate.wizard'

    project = fields.Many2one(comodel_name='project.project', readonly=True)
    project_name = fields.Char(related='project.name', readonly=True)
    project_date = fields.Char(readonly=True)
    project_calculation_type = fields.Selection(
        related='project.calculation_type', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(ProjectRecalculateWizard, self).default_get(fields)
        res['project'] = self.env.context.get('active_id', False)
        project = self.env['project.project'].browse(res['project'])
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
        return self.project.project_recalculate()
