# -*- coding: utf-8 -*-
# (c) 2015 Incaser Informatica S.L. - Sergio Teruel
# (c) 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project Task Default Stage',
    'summary': 'Recovery default task stage projects from v8',
    'version': '9.0.1.0.0',
    'category': 'Project',
    'author': 'Incaser Informatica S.L., '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_view.xml',
        'data/project_data.xml',
    ],
    'installable': True,
}
