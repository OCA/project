import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _logger.info("Turning off rule")
    env.ref("project.project_task_rule_portal").write({"active": False})


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Turning on rule")
    env.ref("project.project_task_rule_portal").write({"active": True})
