# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Earned Value",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": """Open Source Integrators,
        Serpent Consulting Services,
        Odoo Community Association (OCA)""",
    "summary": """This module adds measures to the Task Analysis report and
        provides a basic Earned Value Analysis on the project overview.""",
    "category": "Project",
    "maintainers": ["Khalid-SerpentCS"],
    "website": "https://github.com/OCA/project",
    'depends': [
        "project",
        "sale_timesheet"
    ],
    "data": [
        "views/project_views.xml",
        "report/project_report_views.xml",
    ],
    "qweb": [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
