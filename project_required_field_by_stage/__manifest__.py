# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Required Field By Stage",
    "summary": """
        This module adds checks to allow certain stages to be set only if
        some fields are populated. After install every stage can have
        mandatory fields associated.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "depends": ["project"],
    "data": [
        "views/project_task_type.xml",
    ],
    "demo": [],
    "installable": True,
}
