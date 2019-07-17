# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Recalculate Hour",
    "version": "10.0.1.0.0",
    "author": "Efatto.it, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "category": "Project",
    "depends": [
        'hr_timesheet',
        'project_recalculate',
    ],
    'data': [
        "views/project_task_view.xml",
    ],
    'installable': True,
}
