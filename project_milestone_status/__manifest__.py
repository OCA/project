# Copyright 2025 Lansana Barry Sow(APSL-Nagarro)<lbarry@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Milestone Status",
    "version": "18.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "Lansana Barry Sow, APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["lbarry-apsl"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
        "hr_timesheet",
    ],
    "data": [
        "views/project_milestone_views.xml",
        "views/project_views.xml",
    ],
}
