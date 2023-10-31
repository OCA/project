# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Service tracking: Copy tasks in project",
    "summary": "Copy tasks into sale order's project",
    "version": "14.0.1.0.0",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["shide", "EmilioPascual"],
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": ["sale_project"],
    "data": [
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
