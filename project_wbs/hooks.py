import logging

logger = logging.getLogger(__name__)


def pre_init_hook(env):
    # avoid crashing installation because of having same complete_wbs_code
    for aa in (
        env["account.analytic.account"]
        .with_context(active_test=False)
        .search([("code", "=", False)])
    ):
        aa._write(
            {"code": env["ir.sequence"].next_by_code("account.analytic.account.code")}
        )
    logger.info("Assigning default code to existing analytic accounts")

    # analytic_account_id was removed from project.project in Odoo 17+.
    # Only run this migration block if the column exists in the DB
    # (i.e. when upgrading from an older Odoo version).
    env.cr.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'project_project'
        AND column_name = 'analytic_account_id'
        """
    )
    if env.cr.fetchone():
        projects = (
            env["project.project"]
            .with_context(active_test=False)
            .search([("analytic_account_id", "=", False)])
        )
        projects._create_analytic_account()
        projects.filtered(lambda p: not p.active).mapped("analytic_account_id").write(
            {"active": False}
        )
