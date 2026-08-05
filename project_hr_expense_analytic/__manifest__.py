# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Project HR Expense Analytic",
    "version": "19.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Accounting",
    "summary": "Link expenses to a project and a task",
    "development_status": "Beta",
    "depends": [
        "project_hr_expense",
    ],
    "data": [
        "views/hr_expense_views.xml",
    ],
    "website": "https://github.com/OCA/project",
    "installable": True,
    "auto_install": True,
}
