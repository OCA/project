# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Project Task - Copy ID",
    "summary": "Copy ID of the task with a button",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Productivity",
    "website": "https://github.com/OCA/project",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn", "yajo"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "views/project_task_view.xml",
    ],
}
