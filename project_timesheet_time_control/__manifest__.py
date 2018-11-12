# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project timesheet time control',
    'version': '12.0.1.0.0',
    'development_status': 'Mature',
    'category': 'Project',
    'author': 'Tecnativa,'
              'Odoo Community Association (OCA)',
    'maintainers': ['ernestotejeda'],
    'website': 'https://github.com/OCA/project',
    'depends': [
        'hr_timesheet_task_stage',
        'hr_timesheet_task_domain',
    ],
    'data': [
        'views/account_analytic_line_view.xml',
        'views/project_task_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
