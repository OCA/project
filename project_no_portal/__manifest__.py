# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Project No Portal",
    "summary": "Block portal access on project.project and project.task",
    "version": "18.0.1.0.0",
    "category": "Project",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["divad1196"],
    "license": "AGPL-3",
    "depends": [
        "project",
    ],
    "website": "https://github.com/OCA/project",
    "data": [
        "views/res_config_settings_views.xml",
        "views/project_task_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
}
