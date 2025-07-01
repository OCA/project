# Copyright 2025 APSL Nagarro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project FTE",
    "summary": "Manage FTE (Full-Time Equivalent) contracts and evolution in projects.",
    "version": "17.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "APSL Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["miquelalzanillas", "mpascuall"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
        "project_role",
        "hr_timesheet",
        "hr_timesheet_type_non_billable",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/templates/mail_template.xml",
        "data/ir_cron.xml",
        "wizard/project_fte_mass_generator_views.xml",
        "views/project_fte_month_line_views.xml",
        "views/project_project_views.xml",
        "views/project_role.xml",
        "views/project_milestone.xml",
    ],
}
