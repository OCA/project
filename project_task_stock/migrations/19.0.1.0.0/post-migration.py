# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    legacy_column = openupgrade.get_legacy_name("group_id")
    if openupgrade.column_exists(env.cr, "project_task", legacy_column):
        openupgrade.logged_query(
            env.cr,
            sql.SQL(
                """
                UPDATE project_task
                   SET reference_id = {legacy_column}
                 WHERE {legacy_column} IS NOT NULL
                """
            ).format(legacy_column=sql.Identifier(legacy_column)),
        )
