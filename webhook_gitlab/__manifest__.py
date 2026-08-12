# Copyright 2018, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Webhook for Gitlab",
    "summary": "Link GitHub/GitLab commits, branches and pull requests"
    " to project tasks through webhooks",
    "version": "17.0.1.0.0",
    "category": "Development",
    "author": "Jarsa, Francesco Ballerini, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "maintainers": ["FrancescoBallerini"],
    "development_status": "Beta",
    "license": "LGPL-3",
    "depends": [
        "project",
        "queue_job_cron_jobrunner",
    ],
    "data": [
        "views/message_templates.xml",
        "data/ir_config_parameter.xml",
        "data/project_tags_data.xml",
        "views/git_branch_view.xml",
        "views/git_commit_view.xml",
        "views/git_pull_request_view.xml",
        "views/git_menu.xml",
        "views/project_task_view.xml",
        "views/project_project_view.xml",
        "views/res_users_view.xml",
        "security/ir.model.access.csv",
    ],
    "external_dependencies": {
        "python": [
            "python-gitlab",
            "PyGithub",
        ],
    },
}
