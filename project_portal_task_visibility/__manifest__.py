{
    "name": "Project Portal Task Visibility",
    "version": "16.0.1.1.0",
    "depends": [
        "project",
        "portal",
    ],
    "website": "https://github.com/OCA/project",
    "author": "PyTech SRL, Odoo Community Association (OCA)",
    "category": "Project",
    "license": "AGPL-3",
    "data": ["security/project_portal_task_security.xml"],
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
