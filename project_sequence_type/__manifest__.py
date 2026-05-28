# Copyright 2026 Ledo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Sequence by Type",
    "summary": "Give projects a different sequence depending on their type",
    "version": "18.0.1.0.0",
    "category": "Services/Project",
    "development_status": "Alpha",
    "website": "https://github.com/OCA/project",
    "author": "Ledo, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["project_sequence", "project_type"],
    "data": [
        "views/project_project_views.xml",
        "views/project_type_views.xml",
    ],
}
