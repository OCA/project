# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project FTE",
    "summary": "",
    "version": "17.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
    ],
    "data": [
        "views/project_project_views.xml",
        "security/ir.model.access.csv",
    ],
}
