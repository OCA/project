# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Budget Threshold Alert",
    "summary": """Send notification when project budget threshold is exceeded""",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "depends": ["project", "project_account_budget"],
    "data": [
        "views/res_users.xml",
        "views/project_project.xml",
        "data/cron.xml",
        "data/mail_template.xml",
    ],
    "demo": [],
}
