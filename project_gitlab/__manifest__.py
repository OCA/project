# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Project GitLab",
    "summary": "GitLab bridge for the Project Git connector",
    "version": "17.0.1.0.0",
    "category": "Project",
    "author": "Jarsa, Francesco Ballerini, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "maintainers": ["FrancescoBallerini"],
    "development_status": "Beta",
    "license": "LGPL-3",
    "depends": [
        "project_git",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "data/project_tags_data.xml",
        "views/project_project_view.xml",
        "views/res_users_view.xml",
    ],
    "external_dependencies": {
        "python": [
            "python-gitlab",
        ],
    },
}
