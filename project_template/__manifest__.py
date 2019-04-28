# -*- coding: utf-8 -*-
# Copyright 2019 Thore Baden
# Copyright 2019 Benjamin Brich
{
    'name': 'Project Template',
    'version': '10.0.1.0.0',
    'summary': 'Create Templates for Projects',
    'category': 'Project Management',
    'website': 'https://github.com/OCA/project',
    'author': 'Thore Baden, '
              'Benjamin Brich, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_project_view.xml',
    ],
    'installable': True,
    'application': False,
}
