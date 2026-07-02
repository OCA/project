# Copyright 2026 Patryk Pyczko (Nagarro)<patryk.pyczko@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Post-sale Automation",
    "version": "17.0.1.0.0",
    "summary": "Automate recurring post-sale opportunities from projects",
    "website": "https://github.com/OCA/project",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["project", "crm", "sales_team"],
    "data": [
        "data/ir_cron.xml",
        "views/project_views.xml",
    ],
}
