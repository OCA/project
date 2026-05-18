# Copyright 2025 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Project Task Default User",
    "summary": "Auto assign default users to tasks or when changing task stages",
    "version": "19.0.1.0.0",
    "category": "Project",
    "author": "NICO SOLUTIONS - ENGINEERING & IT, Odoo Community Association (OCA)",
    "maintainers": ["NICO-SOLUTIONS"],
    "website": "https://github.com/OCA/project",
    "depends": ["project"],
    "data": [
        "views/project_project_views.xml",
        "views/project_task_type_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
