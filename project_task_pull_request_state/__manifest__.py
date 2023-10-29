# Copyright Cetmix OU 2023
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Project Task Pull Request State",
    "summary": "Track Pull Request state in tasks",
    "version": "16.0.1.0.0",
    "category": "Project Management",
    "website": "https://github.com/OCA/project",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project_task_pull_request",
    ],
    "data": [
        "views/project_task_view.xml",
        "views/project_project_view.xml",
        "views/res_config_settings_view.xml",
    ],
}
