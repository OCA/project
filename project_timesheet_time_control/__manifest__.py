# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project timesheet time control',
    'version': '10.0.1.0.0',
    'category': 'Project',
    'author': 'Tecnativa,'
              'Odoo Community Association (OCA)',
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'hr_timesheet',
        'project_stage_closed',
    ],
    'data': [
        'views/account_analytic_line_view.xml',
        'views/project_task_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
