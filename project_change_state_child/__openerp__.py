# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Change State Child",
    "version": "9.0.1.0.0",
    'license': 'AGPL-3',
    'author': 'Eficent, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.github.com/OCA/project',
    "category": "Projects",
    "summary": """
        Change the status of multiple projects and its children
        simultaneously.""",
    "depends": [
        "project_wbs",
        "project_change_state"
    ],
    "installable": True
}
