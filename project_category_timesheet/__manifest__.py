# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Timesheet by Category",
    "summary": "Module summary",
    "version": "14.0.1.0.0",
    # Alfa|Beta|Production/Stable|Mature
    "development_status": "Beta",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "ALBA Software," "Odoo Community Association (OCA)",
    # see https://odoo-community.org/page/maintainer-role for a description of the maintainer role and responsibilities
    "license": "AGPL-3",
    "depends": [
        "project_category",
        "hr_timesheet",
    ],
    "data": [
        #"security/some_model_security.xml",
        #"security/ir.model.access.csv",
        "views/project_type_views.xml",
        "views/project_views.xml",
        "views/hr_timesheet_view.xml",
    ],
    "application": False,
    "auto_install": True,   
}
