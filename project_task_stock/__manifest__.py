# Copyright 2022-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Task Stock",
    "version": "18.0.1.0.1",
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
        "views/stock_scrap_views.xml",
    ],
    "demo": [
        "demo/stock_picking_type_data.xml",
        "demo/project_data.xml",
    ],
    "maintainers": ["victoralmau"],
}
