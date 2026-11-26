# Copyright 2026 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Project Task QA Checklist",
    "summary": "Configurable acceptance-criteria checklist for tasks in QA stages",
    "version": "17.0.1.0.0",
    "category": "Project Management",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["project"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_activity_type_data.xml",
        "views/project_task_qa_checklist_template_views.xml",
        "views/project_task_type_views.xml",
        "views/project_task_views.xml",
    ],
    "demo": [
        "demo/project_task_qa_checklist_demo.xml",
    ],
}
