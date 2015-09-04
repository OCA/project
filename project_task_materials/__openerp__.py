# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project Task Materials',
    'summary': 'Record products spent in a Task',
    'version': '1.0',
    'category': "Project Management",
    'author': 'Daniel Reis, '
              'Antiun Ingeniería S.L., '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'description': "",
    'depends': ['project', 'stock', 'stock_account', 'analytic'],
    'data': [
        'data/project_task_materials_data.xml',
        'views/project_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
