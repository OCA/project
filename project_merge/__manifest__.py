# Copyright 2024 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project Task Merge",
    "summary": "Wizard to merge project tasks",
    "version": "18.0.1.0.0",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "category": "Services/Project",
    "depends": ["project"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/project_task_merge_views.xml",
    ],
    "installable": True,
}
