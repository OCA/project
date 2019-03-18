# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Project Hours Blocks Management",
    "version": "11.0.1.0.0",
    "category": "Generic Modules/Projects & Services",
    "description": """
Project Hours Blocks Management
===============================

This module allows you to handle hours blocks,
to follow for example the user support contracts.
This means, you sell a product of type "hours block"
then you input the spent hours on the hours block and
you can track and follow how much has been used.

 """,
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": 'AGPL-3',
    "website": "https://github.com/OCA/project",
    "depends": [
        "account",
        # do we need this? It seems it was merged with contract module
        # "hr_timesheet_invoice",
        "analytic",
        "project",
        ],
    "data": [
        "security/hours_block_security.xml",
        "security/ir.model.access.csv",
        "views/report.xml",
        "views/hours_block_view.xml",
        "views/hours_block_data.xml",
        "views/hours_block_menu.xml",
        "views/product_view.xml",
        "views/project_view.xml",
        "views/report.xml",
    ],
}
