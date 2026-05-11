# Copyright 2026 Innovyou - Lorenzo Battistini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Type to Analytic Plan Synchronization",
    "version": "18.0.1.0.0",
    "category": "Project",
    "summary": "Synchronize the project types hierarchy with analytic plans",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "depends": [
        "account",
        "analytic",
        "project",
        "project_type",
    ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
