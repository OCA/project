# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Tags",
    "summary": "Make tags required on the tasks of a project",
    "author": "Patrick Wilson, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project Management",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["project"],
    "data": [
        "views/project_project_views.xml",
        "views/project_task_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["patrickrwilson"],
}
