# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

{
    "name": "Project Recalculate",
    "version": "8.0.1.0.0",
    "author": "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.antiun.com",
    "license": "AGPL-3",
    "category": "Project",
    "depends": ['project'],
    'data': [
        "views/project_project_view.xml",
        "views/project_task_view.xml",
        "views/project_task_stage_view.xml",
        "wizard/recalculate_wizard.xml",
    ],
    'installable': False,
}
