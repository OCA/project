# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project Multi Department Classification",
    "summary": "This module add a link between projects and several departments",
    "version": "18.0.1.0.0",
    "author": "INVITU, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "website": "https://github.com/OCA/project",
    "depends": [
        "project",
        "hr",
    ],
    "data": ["security/project_security.xml", "views/project_project_views.xml"],
    "installable": True,
}
