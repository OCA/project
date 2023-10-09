# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Carlos Dauden
# Copyright 2021 Open Source Integrators - Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project timeline",
    "summary": "Timeline view for projects",
    "version": "15.0.1.2.1",
    "category": "Project Management",
    "website": "https://github.com/OCA/project",
    "author": "Tecnativa, Onestein, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["project", "web_timeline"],
    "data": [
        "views/project_project_view.xml",
        "views/project_task_view.xml",
    ],
    "demo": ["demo/project_project_demo.xml", "demo/project_task_demo.xml"],
    "post_init_hook": "populate_date_start",
    "assets": {
        "web.assets_backend": [
            "/project_timeline/static/src/scss/project_timeline.scss"
        ]
    },
}
