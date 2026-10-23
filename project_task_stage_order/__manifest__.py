# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Project Task Stage Order",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "summary": "Allows each project to have its own task stage order",
    "category": "Project",
    "depends": ["project_task_stage_mgmt"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "post_init_hook": "post_init_hook",
    "maintainers": ["ElenaEForgeFlow"],
}
