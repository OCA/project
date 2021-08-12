# Copyright 2021 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Duplicated Task",
    "summary": "Allow to close a task and categorize it as a duplicate.",
    "version": "14.0.1.0.0",
    "category": "Services/Project",
    "website": "https://github.com/OCA/project",
    "author": " Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
    ],
    "data": [
        "data/data.xml",
        "views/duplicated_task_view.xml",
    ],
}
