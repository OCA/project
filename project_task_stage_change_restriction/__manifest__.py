# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Task Stage Change Restriction",
    "summary": "Restrict project task stage",
    "version": "16.0.1.0.0",
    "category": "Project",
    "author": "Odoo Community Association (OCA), Cetmix",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/project",
    "depends": ["project"],
    "data": [
        "views/project_task_stage_views.xml",
    ],
    "demo": [
        "data/demo_project_task_stage.xml",
    ],
    "installable": True,
    "application": False,
}
