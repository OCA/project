# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Stock Product Set",
    "version": "16.0.1.0.0",
    "category": "Project Management",
    "website": "https://github.com/OCA/project",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["project_stock", "sale_product_set"],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "wizard/product_set_add.xml",
        "views/project_task_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
