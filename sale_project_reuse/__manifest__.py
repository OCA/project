# Copyright 2026 glueckkanja AG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sale Project Reuse",
    "summary": "Reuse the customer's project on sale orders",
    "version": "19.0.1.0.0",
    "author": "glueckkanja AG, Odoo Community Association (OCA)",
    "maintainers": ["CRogos"],
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": ["sale_project"],
    "data": [
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
}
