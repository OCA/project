# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Group Hr Timesheet",
    "summary": """This module makes project group work properly with timesheets""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "depends": [
        "project_group",
        "hr_timesheet",
    ],
    "auto_install": True,
    "data": ["security/security.xml"],
}
