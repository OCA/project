# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Stock",
    "version": "13.0.2.2.1",
    "category": "Project Management",
    "website": "https://github.com/OCA/project",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["project", "stock"],
    "installable": True,
    "data": [
        "views/project_project_view.xml",
        "views/project_task_type_view.xml",
        "views/stock_move_view.xml",
        "views/project_task_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
