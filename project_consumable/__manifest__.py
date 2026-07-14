# Copyright 2021-2025 - Pierre Verkest
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Project consumable",
    "summary": "Track the use of consumables by project with analytic accounting.",
    "author": "Pierre Verkest, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project Management",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["petrus-v"],
    "depends": [
        "account",
        "hr_timesheet",
    ],
    "data": [
        "views/analytic_account_line.xml",
        "views/analytic_account_line_report.xml",
        "views/product.xml",
        "views/project_views.xml",
        "security/project_consumable_security.xml",
    ],
    "demo": [
        "demo/product-product.xml",
    ],
    "post_init_hook": "set_project_ok_for_consumable_products",
}
