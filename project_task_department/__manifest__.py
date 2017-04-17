# -*- coding: utf-8 -*-
# © 2011 Joël Grand-Guillaume (Camptocamp)
# © 2013 Daniel Reis (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Task specific Department",
    "version": "10.0.1.0.0",
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
    "data": ["views/project.xml"],
    'installable': True,
}
