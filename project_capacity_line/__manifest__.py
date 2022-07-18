# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project Capacity Lines",
    "summary": "Project Capacity Lines",
    "version": "15.0.1.0.0",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "depends": [
        "base",
        "sale_timesheet",
        "hr_holidays",
    ],
    "data": [
        "security/capacity_line_security.xml",
        "security/ir.model.access.csv",  # TO FIX
        "views/sale_order_views.xml",
        "views/hr_employee_views.xml",
        "views/capacity_line_views.xml",
        "views/capacity_role_views.xml",
        "views/product_views.xml",
        "views/project_task_views.xml",
        "views/project_project_stage_views.xml",
        "views/res_config_settings_views.xml",
        "data/ir_cron.xml",
        "data/project_data.xml",
    ],
    "installable": True,
}
