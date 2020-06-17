# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Task Send By Mail",
    "summary": "Send task report by email",
    "version": "13.0.1.0.0",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project Management",
    "license": "AGPL-3",
    "depends": ["project_task_report"],
    "data": ["views/project_task_views.xml", "data/task_template.xml"],
    "installable": True,
}
