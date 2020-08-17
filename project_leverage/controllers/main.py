# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.http import request
from odoo.exceptions import UserError

from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController


DEFAULT_MONTH_RANGE = 3


class SaleTimesheetController(SaleTimesheetController):

    def _plan_prepare_values(self, projects):

        employee_obj = request.env['hr.employee']
        values = super(SaleTimesheetController,
                       self)._plan_prepare_values(projects)
        _select = self.select_line()
        _from = self.line_from()
        _where = self.line_where(projects.ids)
        _group = self.line_group()
        query = _select + _from + _where + _group
        request.env.cr.execute(query)
        raw_data = request.env.cr.dictfetchall()
        project_data = {}
        month_list = []
        month_name_list = []
        for rec in raw_data:
            if str(rec.get('month')).strip() + ' ' + str(
                    int(rec.get('year'))) not in month_name_list:
                month_name_list.append(
                    str(rec.get('month')).strip() + ' ' + str(
                        int(rec.get('year'))))
            if str(rec.get('date_mm')).strip() + str(
                    int(rec.get('year'))) not in month_list:
                month_list.append(
                    str(rec.get('date_mm')).strip() + str(
                        int(rec.get('year'))))
            if project_data.get(rec.get('employee_id') or 0):
                project_data[rec.get('employee_id') or 0].update(
                    {str(rec.get('date_mm')).strip() + str(
                        int(rec.get('year'))): {'name':
                                                employee_obj.browse(int(
                                                    rec.get(
                                                        'employee_id'))).name,
                                                'month_name': rec.get('month'),
                                                'hours': rec.get('sum'),
                                                }})
            else:
                project_data.update({rec.get('employee_id') or 0: {
                    str(rec.get('date_mm')).strip() + str(
                        int(rec.get('year'))): {'month_name': rec.get('month'),
                                                'hours': rec.get('sum'),
                                                },
                    'name': rec.get('employee_id') and employee_obj.browse(
                        int(rec.get('employee_id'))).name or "undefine"
                }, })
        values['month_name_list'] = month_name_list
        values['month_list'] = month_list
        values['leverage'] = project_data
        return values

    def select_line(self):
        select_str = """
            Select to_char(date , 'Month') as month, sum(unit_amount),
            EXTRACT(YEAR FROM date) AS Year, to_char(date, 'MM') as date_mm,
            employee_id
        """
        return select_str

    def line_from(self):
        return """
            FROM account_analytic_line
        """

    def line_where(self, project_ids):
        project_mananger_ids = [
            project.user_id.id
            for project in request.env['project.project'].browse(project_ids)]
        employee_ids = request.env['hr.employee'].search(
            [('user_id', 'in', project_mananger_ids),
             ('user_id', '!=', False)])
        query = """
            WHERE
        """
        if not employee_ids:
            raise UserError('Project Manager is not defined or no '
                            'timesheet entry found for project manager.')
        if len(project_ids) > 1 and len(employee_ids) > 1:
            query += """
                project_id IN %s AND employee_id IN %s AND is_manager IS %s
            """ % (str(tuple(project_ids)),
                   str(tuple(employee_ids.ids)), 'TRUE')
        elif len(project_ids) > 1 and len(employee_ids) == 1:
            query += """
                project_id IN %s AND employee_id = %s AND is_manager IS %s
            """ % (str(tuple(project_ids)), str(employee_ids.id), 'TRUE')
        else:
            query += """
                project_id = %s AND employee_id = %s AND is_manager IS %s
            """ % (str(project_ids[0]), str(employee_ids.id), 'TRUE')
        return query

    def line_group(self):
        return """
            group by Year, month, date_mm, employee_id order by month
        """
