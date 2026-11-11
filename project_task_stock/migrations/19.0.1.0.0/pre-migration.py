# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "project_task", "group_id"):
        openupgrade.copy_columns(env.cr, {"project_task": [("group_id", None, None)]})
