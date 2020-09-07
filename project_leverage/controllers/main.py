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
        _where = self.line_where(projects)
        _group = self.line_group()
        query = _select + _from + _where + _group
        request.env.cr.execute(query)
        raw_data = request.env.cr.dictfetchall()
        project_data = {}
        month_list = []
        month_name_list = []
        for rec in raw_data:
            month_name_list.append(rec.get('month_year'))
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
            CONCAT(to_char(date , 'Month'), EXTRACT(YEAR FROM date))
            AS month_year, employee_id
        """
        return select_str

    def line_from(self):
        return """
            FROM account_analytic_line
        """

    def line_where(self, projects):
        project_mananger_ids = projects.mapped('user_id')
        employee_ids = request.env['hr.employee'].search(
            [('user_id', 'in', project_mananger_ids.ids),
             ('user_id', '!=', False)])
        query = ""
        if not employee_ids:
            raise UserError('Project Manager is not defined or no '
                            'timesheet entry found for project manager.')
        if projects and employee_ids:
            query += """
                WHERE project_id IN %s AND employee_id IN %s
            """ % ([tuple(projects.ids)], [tuple(employee_ids.ids)])
        return query

    def line_group(self):
        return """
            group by Year, month, date_mm, employee_id order by month, Year
        """
