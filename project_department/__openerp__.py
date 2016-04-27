# -*- coding: utf-8 -*-
# © 2014 Joël Grand-Guillaume (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Department Categorization",
    "version": "9.0.1.0.0",
    "author": "Camptocamp, Daniel Reis,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "description": """\
Add Department to Projects and task to corresponding tree, search and form
views.
""",
    "website": "http://camptocamp.com",
    "depends": [
        "analytic_base_department",
        "project",
    ],
    "data": ["views/project.xml"],
    "auto_install": True,
    'installable': True,
}
