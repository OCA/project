# Copyright 2024 Binhex - Adasat Torres de León (https://www.binhex.cloud)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Scrum",
    "version": "16.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "Binhex, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "This addon allow use the scrum methodology in projects",
    "depends": ["project_timeline"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_sprint_views.xml",
        "views/project_views.xml",
        "data/ir_cron_data.xml",
    ],
    "maintainers": ["adasatorres"],
}
