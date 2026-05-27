{
    "name": "Project Task Planning",
    "version": "19.0.1.0.0",
    "category": "Services/Project",
    "summary": """
        Personalized planning of hours for tasks and projects
        without economic values or timesheets.
    """,
    "author": "Odoo Community Association (OCA), SDi",
    "website": "https://github.com/OCA/project",
    "depends": [
        "project",
        "project_timeline",
        "hr",
        "hr_holidays",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "data/ir_cron_data.xml",
        "views/project_project_views.xml",
        "views/project_task_views.xml",
        "views/project_task_allocation_views.xml",
        "views/project_task_planning_views.xml",
        "views/hr_employee_bucket_views.xml",
        "views/hr_employee_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}
