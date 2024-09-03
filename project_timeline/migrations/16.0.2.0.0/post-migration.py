# Copyright 2024 Tecnativa - Juan José Seguí
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """UPDATE project_task
        SET planned_date_end = date_end
        WHERE planned_date_end IS NULL AND date_end IS NOT NULL;
        """,
    )
