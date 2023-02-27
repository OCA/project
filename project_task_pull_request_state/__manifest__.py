{
    "name": "Project Task Pull Request State",
    "summary": "Add a field for a PR State to project tasks",
    "version": "11.0.1.0.0",
    "category": "Project Management",
    "website": "https://odoo-community.org/",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project_task_pull_request",
    ],
    "maintainers": ["isserver1", "CetmixGitDrone"],
    "data": [
        "views/project_task_view.xml",
        "views/project_project_view.xml",
    ],
}
