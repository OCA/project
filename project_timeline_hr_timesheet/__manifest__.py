# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Timeline - Timesheet",
    "summary": "Shows the progress of tasks on the timeline view.",
    "author": "Onestein, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/project",
    "category": "Project Management",
    "version": "15.0.1.0.0",
    "depends": ["project_timeline", "hr_timesheet"],
    "data": ["views/project_task_view.xml"],
    "assets": {
        "web.assets_backend": [
            "/project_timeline_hr_timesheet/static/src/scss/project_timeline_hr_timesheet.scss"
        ]
    },
    "installable": True,
    "auto_install": True,
}
