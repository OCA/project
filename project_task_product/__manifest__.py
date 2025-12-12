# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Task Product",
    "summary": "Allows to specify in a project task, the product the task relates to.",
    "version": "19.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["project", "product"],
    "data": [
        "views/project_task_views.xml",
        "views/product_views.xml",
    ],
    "application": False,
    "installable": True,
}
