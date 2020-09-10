# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.http import request

from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController

DEFAULT_MONTH_RANGE = 3


class SaleTimesheetController(SaleTimesheetController):

    def _plan_prepare_values(self, projects):

        projects_obj = request.env['project.project']
        values = super(
            SaleTimesheetController, self)._plan_prepare_values(projects)
        _select = request.env['report.project.task.user']._select()
        _from = request.env['report.project.task.user']._from()
        _where = request.env['report.project.task.user'].with_context(
            project_ids=projects.ids)._where()
        if projects:
            _where += """
                    AND
                    t.project_id IN %s
                """
        param = [tuple(projects.ids)]
        _group_by = request.env['report.project.task.user']._group_by()
        query = _select + _from + _where + _group_by
        request.env.cr.execute(query, param)
        raw_data = request.env.cr.dictfetchall()
        project_data = {}
        for data in raw_data:
            if project_data.get(data.get('project_id')):
                project_data[data.get('project_id')].update({
                    'planned_value':
                    data.get('planned_value') +
                    project_data[data.get('project_id')].get('planned_value'),
                    'earned_value':
                    data.get('earned_value') +
                    project_data[data.get('project_id')].get('earned_value'),
                    'actual_cost':
                    data.get('actual_cost') +
                    project_data[data.get('project_id')].get('actual_cost'),
                    'schedule_variance':
                    data.get('schedule_variance') +
                    project_data[data.get('project_id')].get(
                        'schedule_variance'),
                    'cost_variance':
                    data.get('cost_variance') +
                    project_data[data.get('project_id')].get('cost_variance'),
                })
            else:
                project_data.update({data.get('project_id'): {
                    'name':
                    projects_obj.browse(int(data.get('project_id'))).name,
                    'planned_value': data.get('planned_value'),
                    'earned_value': data.get('earned_value'),
                    'actual_cost': data.get('actual_cost'),
                    'schedule_variance': data.get('schedule_variance'),
                    'cost_variance': data.get('cost_variance'),
                }})
        values['earned_value'] = project_data
        return values
