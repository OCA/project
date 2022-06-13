# Copyright 2020 Advitus MB
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Project Task Team",
    "summary": "Display only Task member related tasks",
    "category": "Project",
    "version": "14.0.1.0.0",
    "author": "Advitus MB, Ooops, Odoo Community Association (OCA)",
    "maintainers": ["AshishHirapara"],
    "website": "https://github.com/OCA/project",
    "license": "LGPL-3",
    "depends": [
        "project",
    ],
    "data": [
        "security/res_groups.xml",
        "views/project_task.xml",
        "views/mail_activity.xml",
    ],
    "installable": True,
}
