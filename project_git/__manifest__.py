# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Project Git",
    "summary": "Link git commits, branches and pull requests"
    " to project tasks through webhooks",
    "version": "17.0.1.0.0",
    "category": "Project",
    "author": "Jarsa, Francesco Ballerini, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "maintainers": ["FrancescoBallerini"],
    "development_status": "Beta",
    "license": "LGPL-3",
    "depends": [
        "project",
        "queue_job",
    ],
    "data": [
        "data/message_templates.xml",
        "data/ir_config_parameter.xml",
        "data/project_tags_data.xml",
        "views/project_git_branch_view.xml",
        "views/project_git_commit_view.xml",
        "views/project_git_pull_request_view.xml",
        "views/project_git_menu.xml",
        "views/project_task_view.xml",
        "views/project_project_view.xml",
        "security/ir.model.access.csv",
    ],
}
