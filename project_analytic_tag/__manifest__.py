# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Analytic Tag",
    "version": "16.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["project", "account_analytic_tag"],
    "installable": True,
    "auto_install": True,
    "data": [
        "views/project_task_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
