# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Estimation",
    "summary": "Pre-sales project cost estimation and margin calculation",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "depends": ["sale_project"],
    "data": [
        "data/sequence.xml",
        "security/project_estimation_security.xml",
        "security/ir.model.access.csv",
        "wizard/create_sale_order_view.xml",
        "views/project_estimation_views.xml",
        "views/sale_order_view.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["Saran440"],
}
