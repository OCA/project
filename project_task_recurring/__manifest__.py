# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Recurring Task",
    "summary": """
        Allows to add recurring tasks to a project""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "depends": ["project", "project_template", "base_recurrence"],
    "data": [
        "security/project_task_schedule.xml",
        "views/project_project.xml",
        "views/project_task_schedule.xml",
        "data/ir_cron.xml",
    ],
    "demo": [
        "demo/project_project.xml",
        "demo/project_task.xml",
        "demo/project_task_schedule.xml",
    ],
}
