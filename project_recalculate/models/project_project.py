# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2014 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
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

from openerp import models, fields
from openerp.exceptions import Warning
from openerp.tools.translate import _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    calculation_type = fields.Selection(
        [('date_begin', 'Date begin'), ('date_end', 'Date end')],
        default='date_begin', string='Calculation type',
        help='How to calculate tasks with date start or date end references')

    def calcule_date_start_date_end(self):
        vals = {}
        project_task_obj = self.env['project.task']
        project_task_ids = project_task_obj.search(
            [('project_id', '=', self.id)])
        date_start = (fields.Datetime.from_string(self.date_start)
                      if self.date_start
                      else fields.Datetime.from_string(self.date))
        date_end = (fields.Datetime.from_string(self.date)
                    if self.date
                    else fields.Datetime.from_string(self.date_start))
        if len(project_task_ids) > 0:
            min_date_start = fields.Datetime.from_string(
                project_task_ids[0].date_start)
            max_date_start = fields.Datetime.from_string(
                project_task_ids[0].date_start)
            max_date_end = fields.Datetime.from_string(
                project_task_ids[0].date_end)
            date_start = fields.Datetime.from_string(
                project_task_ids[0].date_start)
            for project_task in project_task_ids:
                if not project_task.date_start and project_task.date_end:
                    project_task.date_start = project_task.date_end
                if not project_task.date_end and project_task.date_start:
                    project_task.date_end = project_task.date_start
                if not project_task.date_start or not project_task.date_end:
                    continue
                date_start = fields.Datetime.from_string(
                    project_task.date_start)
                date_end = fields.Datetime.from_string(project_task.date_end)
                if min_date_start > date_start:
                    min_date_start = date_start
                if max_date_end < date_end:
                    max_date_end = date_end
                if max_date_start < date_start:
                    max_date_start = date_end
            if self.calculation_type == 'date_begin':
                vals['date'] = max_date_end
            else:
                vals['date_start'] = min_date_start
        self.write(vals)

    def project_recalculate(self):
        if not self.calculation_type:
            raise Warning(_("Cannot recalculate project because your project "
                            "don't have calculation type."))
        if self.calculation_type == 'date_begin' and not self.date_start:
            raise Warning(_("Cannot recalculate project because your project "
                            "don't have date start."))
        if self.calculation_type == 'date_end' and not self.date:
            raise Warning(_("Cannot recalculate project because your project "
                            "don't have date end."))
        project_task_obj = self.env['project.task']
        project_task_type_obj = self.env['project.task.type']
        project_task_type = project_task_type_obj.search([('fold', '=', True)])
        project_task_type_ids = [x.id for x in project_task_type]
        project_task_ids = project_task_obj.search(
            [('project_id', '=', self.id),
             ('stage_id', 'not in', project_task_type_ids)
             ])
        for task in project_task_ids:
            if not task.stage_id.fold:
                task.with_context(
                    self.env.context,
                    project_recalculate=True).task_recalculate()
        self.calcule_date_start_date_end()
