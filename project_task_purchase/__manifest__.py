# Copyright 2023 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Project Task Purchase",
    "summary": "Create purchase orders from project tasks",
    "version": "17.0.1.0.0",
    "category": "Project Management",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["project", "purchase"],
    "data": [
        "security/res_groups.xml",
        "views/project_task_view.xml",
        "views/purchase_order_view.xml",
    ],
}
