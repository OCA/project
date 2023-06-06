# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Project timesheet time control",
    "version": "13.0.1.1.1",
    "development_status": "Mature",
    "category": "Project",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "maintainers": ["ernestotejeda"],
    "website": "https://github.com/OCA/project",
    "depends": [
        "hr_timesheet_task_stage",
        "hr_timesheet_task_domain",
        "web_ir_actions_act_multi",
        "web_ir_actions_act_view_reload",
    ],
    "data": [
        "views/account_analytic_line_view.xml",
        "views/project_project_view.xml",
        "views/project_task_view.xml",
        "wizards/hr_timesheet_switch_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "post_init_hook": "post_init_hook",
}
