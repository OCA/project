# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Project Task Stage Lock",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "summary": """
    Locks the Stages in the Kanban view of the project task
    to avoid modification of the stages in other projects.

    Also removes the default group by in the stages list view
    to be able to see the stages order.
    """,
    "website": "https://github.com/OCA/project",
    "category": "Project",
    "depends": ["project"],
    "data": [
        "views/project.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "project_task_stage_lock/static/src/views/project_task_kanban_renderer.esm.js",
        ],
    },
    "license": "AGPL-3",
    "installable": True,
    "maintainers": ["DavidJForgeFlow"],
}
