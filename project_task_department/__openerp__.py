# -*- coding: utf-8 -*-
{
    "name": "Project Task specific Department",
    "version": "8.0.1.0.0",
    "author": "Daniel Reis,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "description": """\
Enables Tasks to store the Department they correspond to.
By default this will be the Project Department, but it is editable.

(Note that the ``project_department`` also adds a Department field on
Tasks, but with the sole purpose of making the Project Department
available on them.)
""",
    "website": "https://github.com/OCA/project-service",
    "depends": [
        "project_department",
    ],
    "data": ["project_view.xml"],
    "installable": True,
}
