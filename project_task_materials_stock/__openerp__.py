# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project Task Materials Stock',
    'summary': 'Create stock and analytic moves from '
               'record products spent in a Task',
    'version': '8.0.1.0.0',
    'category': "Project Management",
    'author': 'Antiun Ingeniería S.L., '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['stock_account', 'project_task_materials'],
    'data': [
        'data/project_task_materials_data.xml',
        'views/project_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
