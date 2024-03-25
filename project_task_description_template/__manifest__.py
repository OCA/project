# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Project Task Templates",
    "version": "14.0.1.0.0",
    "summary": "Module for Task Templates",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "category": "Project",
    "maintainers": ["aleuffre", "renda-dev"],
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "depends": ["project"],
    "demo": [
        "data/demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task_template_views.xml",
        "views/project_views.xml",
        "views/assets.xml",
    ],
    "application": False,
}
