# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Portal Properties",
    "summary": """Show project properties in Portal""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "depends": ["project", "web_portal_properties"],
    "data": [
        "views/project_task.xml",
        "views/project_task_portal_template.xml",
    ],
    "demo": [],
}
