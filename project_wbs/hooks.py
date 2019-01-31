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

    cr.execute(
        """
        SELECT id FROM project_project
        """
    )
    for pp in cr.fetchall():
        cr.execute(
            """
            INSERT INTO account_analytic_account (name,company_id,code)
            SELECT name, company_id, name
            FROM project_project
            WHERE project_project.id=%s
            RETURNING account_analytic_account.id
            """,
            (tuple(pp,))
            # % pp[0]
        )
        aa2 = cr.fetchone()
        cr.execute(
            """
            UPDATE project_project set analytic_account_id=%s WHERE id=%s
            """,
            (tuple(aa2,), tuple(pp,)))
        # % (aa2[0], pp[0]))
