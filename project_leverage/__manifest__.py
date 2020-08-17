# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Leverage",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": """Open Source Integrators,
        Serpent Consulting Services,
        Odoo Community Association (OCA)""",
    "summary": """This module allows you to report on the leverage of a
        project manager. It supports changes of Project Manager.""",
    "category": "Project",
    "maintainers": ["Khalid-SerpentCS"],
    "website": "https://github.com/OCA/project",
    "depends": [
        "project",
        "sale_timesheet"
    ],
    "data": [
        "views/account_analytic_view.xml",
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
