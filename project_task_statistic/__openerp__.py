# -*- coding: utf-8 -*-
# Copyright 2014 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Task Statistics',
    'summary': 'Add a new tab Statistics to the task form',
    'license': 'AGPL-3',
    'version': '8.0.1.0.0',
    'category': 'Project Management',
    'author': 'Daniel Reis, Odoo Community Association (OCA)',
    'depends': [
        'project_stage_state',
    ],
    'data': [
        'views/project_task_views.xml',
    ],
    'installable': True,
}
