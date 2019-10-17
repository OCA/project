from odoo.api import Environment, SUPERUSER_ID
import logging

logger = logging.getLogger(__name__)


def create_analytic_account(env, projects):
    for project in projects:
        analytic_account = env["account.analytic.account"].create(
            {
                "name": project.name,
                "company_id": project.company_id.id,
                "partner_id": project.partner_id.id,
                "active": True,
            }
        )
        project.write({"analytic_account_id": analytic_account.id})


def pre_init_hook(cr):
    env = Environment(cr, SUPERUSER_ID, {})
    # avoid crashing installation because of having same complete_wbs_code
    for aa in env["account.analytic.account"].with_context(
            active_test=False).search([("code", "=", False)]):
        aa._write({"code": env["ir.sequence"].next_by_code(
            "account.analytic.account.code")})
    logger.info("Assigning default code to existing analytic accounts")
    projects = (
        env["project.project"]
        .with_context(active_test=False)
        .search([("analytic_account_id", "=", False)])
    )
    create_analytic_account(env, projects)
    projects.filtered(lambda p: not p.active).mapped(
        "analytic_account_id"
    ).write({"active": False})
