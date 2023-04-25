{
    "name": "Project Administrator Restricted Visibility",
    "version": "13.0.1.0.0",
    "summary": "Adds a 'Project Administrator' access group "
    "with restricted visibility to 'Projects'",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "category": "Project",
    "depends": ["project"],
    "data": ["security/project_security.xml"],
    "uninstall_hook": "uninstall_hook",
}
