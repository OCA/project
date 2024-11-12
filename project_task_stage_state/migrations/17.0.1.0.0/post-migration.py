# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task AS task
        SET state = task_type.task_state
        FROM project_task_type AS task_type
        WHERE task.stage_id = task_type.id
        AND task_type.task_state IS NOT NULL
        AND task.state != task_type.task_state
        """,
    )
