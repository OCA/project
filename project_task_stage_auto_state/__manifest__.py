# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Project Task Stage Auto State",
    "summary": "Auto-change task state (done/canceled) after N days on selected stages",
    "version": "19.0.1.0.1",
    "development_status": "Alpha",
    "category": "Productivity/Project",
    "website": "https://github.com/OCA/project",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
    ],
    "external_dependencies": {
        "python": ["freezegun"],
    },
    "data": [
        "data/ir_cron_data.xml",
        "views/project_task_type_view.xml",
    ],
}
