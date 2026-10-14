import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

views_to_switch = [
    "hr_timesheet.portal_tasks_list_inherit",
    "hr_timesheet.portal_timesheet_table",
    "hr_timesheet.portal_my_task",
    "sale_timesheet.portal_my_task_inherit",
]


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Turning off views")
    env["ir.ui.view"].search([("key", "in", views_to_switch)]).write({"active": False})


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Turning on views")
    env["ir.ui.view"].search(
        [("key", "in", views_to_switch), ("active", "=", False)]
    ).write({"active": True})
