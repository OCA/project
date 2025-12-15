# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Task Product Stock",
    "summary": "Allows to specify in a project task, the lot or serial number of"
    " the task product.",
    "version": "19.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["project_task_product", "project_stock"],
    "data": [
        "views/project_task_views.xml",
        "views/stock_lot_views.xml",
    ],
    "application": False,
    "installable": True,
}
