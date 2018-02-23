# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

{
    "name": "Project Git",
    "summary": "Integrates your projects with git based services",
    "category": "Project",
    "version": "11.0.1.0.0",
    "license": "LGPL-3",
    "author": "Odoo Community Association (OCA), Modoolar",
    "website": "https://www.modoolar.com/",
    "depends": [
        "project_key",
        "web_widget_image_url",
    ],
    "data": [
        "data/mail_message.xml",

        "security/ir.model.access.csv",

        "views/project_git_commit_views.xml",
        "views/project_git_user_views.xml",
        "views/project_git_branch_views.xml",
        "views/project_git_repository_views.xml",
        "views/project_project_views.xml",
        "views/project_task_views.xml",
        "views/menu_views.xml",
    ],

    "demo": [],
    "qweb": [
        "static/src/xml/agile_git.xml",
    ],
    "application": False,
    "installable": True,
}
