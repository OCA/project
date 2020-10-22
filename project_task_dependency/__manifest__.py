# Copyright 2016-2020 Onestein (<http://www.onestein.eu>)
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Task Dependencies",
    "version": "14.0.1.0.0",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "summary": "Enables to define dependencies (other tasks) of a task",
    "author": "Onestein,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["astirpe"],
    "depends": ["project"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
