# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Task Digitized Signature",
    "version": "16.0.1.0.0",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project Management",
    "license": "AGPL-3",
    "depends": ["project_task_report"],
    "data": [
        "security/project_task_digitized_signature_security.xml",
        "views/res_config_settings_views.xml",
        "report/project_task_report.xml",
        "views/project_task_views.xml",
    ],
    "installable": True,
}
