# -*- coding: utf-8 -*-
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project issue timesheet time control',
    'version': '10.0.1.0.0',
    'category': 'Project Management',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'project_timesheet_time_control',
        'project_issue_sheet',
    ],
    'data': [
        'views/account_analytic_line_view.xml',
        'views/project_issue_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': True,
}
