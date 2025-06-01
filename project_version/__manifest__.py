# Copyright 2025 Lansana Barry Sow(APSL-Nagarro)<lbarry@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Version",
    "version": "18.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "Lansana Barry Sow, APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["lbarry-apsl"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_project_views.xml",
        "views/project_task_views.xml",
        "views/project_version_views.xml",
    ],
}
