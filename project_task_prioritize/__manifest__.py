# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Task Prioritize",
    "summary": "Allows to define a task prioritizer format.",
    "version": "18.0.1.0.0",
    "category": "Project",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "contributors": ["DavidJForgeFlow"],
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "depends": ["project", "web_widget_x2many_2d_matrix"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/project_task_prioritizer_view.xml",
        "views/project_view.xml",
        "views/prioritizer_category_views.xml",
    ],
    "demo": ["demo/prioritizer_category_data.xml"],
    "installable": True,
}
