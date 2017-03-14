# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Task Configurable Category",
    "summary": "Allow for Project specific category lists for Tasks",
    "version": "8.0.1.0.1",
    "category": "Project Management",
    "website": "www.elico-corp.com",
    "author": "Elico Corp, Odoo Community Association (OCA)",
    "depends": [
        "project",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/project_task_view.xml',
        'views/task_category_view.xml',
        'data/task_category_demo.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
}
