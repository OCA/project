{
    "name": "Project Portal Hide Timesheet",
    "version": "16.0.1.0.0",
    "depends": [
        "hr_timesheet",
        "portal",
        "sale_timesheet",
    ],
    "website": "https://github.com/OCA/project",
    "author": "PyTech SRL, Odoo Community Association (OCA)",
    "category": "Project",
    "license": "AGPL-3",
    "data": ["views/project_task_templates.xml", "views/timesheet_sheet_templates.xml"],
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
