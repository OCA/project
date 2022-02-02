# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade  # pylint: disable=W7936

from odoo.modules import registry

from odoo.addons.project_timeline.hooks import populate_date_start


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "start_date", "project_task"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE project_task
            ADD COLUMN date_start timestamp""",
        )
    populate_date_start(env.cr, registry)
