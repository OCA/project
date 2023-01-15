# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Time control with time type",
    "summary": "Adds time type in time control forms",
    "version": "14.0.1.0.0",
    # Alfa|Beta|Production/Stable|Mature
    "development_status": "Beta",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "ALBA Software," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        # https://github.com/OCA/project/
        "project_timesheet_time_control",
        # https://github.com/OCA/timesheet/
        "hr_timesheet_time_type",
    ],
    "data": [
        # "security/some_model_security.xml",
        "security/ir.model.access.csv",
        "views/hr_timesheet_view.xml",
        "views/project_time_type_rule_views.xml",
    ],
    "application": False,
    "auto_install": True,
}
