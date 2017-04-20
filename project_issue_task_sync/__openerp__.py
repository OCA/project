# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sync issues and tasks",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Project Management",
    "summary": "Syncronizes tasks and issues",
    "depends": [
        'project_issue'
    ],
    "data": [
        'views/project_project.xml',
        'views/project_task.xml',
    ],
    "installable": True,
}
