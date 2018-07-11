# -*- coding: utf-8 -*-
# Copyright 2018 RGB Consulting <odoo@rgbconsulting.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Project Task Reviewer",
    'version': '10.0.1.0.0',
    'depends': ['project'],
    'license': 'AGPL-3',
    'author': 'RGB Consulting SL, '
              'Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/project",
    'category': 'Project Managment',
    'summary': """Adds project reviewer in project task""",
    'data': [
        'views/project_task_view.xml',
    ],
    'installable': True,
}
