# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Project Template Stage Order",
    "summary": "Link a project to a template so its stages follow it",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project",
    "depends": ["project_template", "project_task_stage_order"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_views.xml",
        "views/project_template_copy_wizard_views.xml",
        "views/project_link_template_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "project_template_stage_order/static/src/views/project_task_kanban_renderer.esm.js",
        ],
    },
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "maintainers": ["ElenaEForgeFlow"],
}
