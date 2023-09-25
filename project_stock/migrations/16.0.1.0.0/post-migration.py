# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """If table exists and there are any records, we set the module
    project_stock_analytic_tag to be installed."""
    if openupgrade.table_exists(env.cr, "account_analytic_tag_project_task_stock_rel"):
        env.cr.execute(
            """SELECT COUNT(*)
            FROM account_analytic_tag_project_task_stock_rel""",
        )
        if env.cr.fetchone()[0]:
            openupgrade.logged_query(
                env.cr,
                """UPDATE ir_module_module
                SET state = 'to install'
                WHERE name = 'project_stock_analytic_tag'""",
            )
