# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Share",
    "summary": """
        Improve the Share view of projects,
        showing the kanban view on readonly too
    """,
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "depends": [
        "project",
    ],
    "data": [
        "views/project_collaborator.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
}
