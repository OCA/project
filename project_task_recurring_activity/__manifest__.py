{
    "name": "Project Task Recurring Activity",
    "summary": """Project Task Recurring Activity""",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project Management",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["project"],
    "data": [
        "security/ir.model.access.csv",
        "views/recurring_activity.xml",
        "views/project_task.xml",
        "data/recurring_activity.xml",
    ],
    "application": False,
    "maintainers": ["dessanhemrayev", "CetmixGitDrone"],
}
