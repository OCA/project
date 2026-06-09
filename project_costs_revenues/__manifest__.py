{
    "name": "Project Costs and Revenues",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "summary": "Pivot report of project timesheet hours, cost, and billable revenue"
    " per period",
    "category": "Services/Project",
    "author": "Innovara, Odoo Community Association (OCA)",
    "maintainers": ["innovara"],
    "license": "AGPL-3",
    "website": "https://github.com/OCA/project",
    "depends": ["project", "hr_timesheet", "sale_timesheet"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_costs_revenues_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
