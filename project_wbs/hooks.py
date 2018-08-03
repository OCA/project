from odoo.api import Environment, SUPERUSER_ID
import logging
logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    env = Environment(cr, SUPERUSER_ID, {})
    # avoid crashing installation because of having same complete_wbs_code
    for aa in env['account.analytic.account'].search([]):
        aa.code = env['ir.sequence'].next_by_code(
            'account.analytic.account.code')
    logger.info('Assigning default code to existing analytic accounts')
