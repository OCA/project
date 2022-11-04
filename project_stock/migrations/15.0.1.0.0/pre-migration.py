# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_table_renamed = [
    (
        "account_analytic_tag_project_task_rel",
        "account_analytic_tag_project_task_stock_rel",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _table_renamed)
