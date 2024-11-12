# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "project.task.type",
                "project_task_type",
                "state",
                "task_state",
            ),
        ],
    )
    # Conver all values to new values
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task_type
        SET task_state = NULL
        WHERE task_state = 'draft'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task_type
        SET task_state = '01_in_progress'
        WHERE task_state = 'open'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task_type
        SET task_state = '04_waiting_normal'
        WHERE task_state = 'pending'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task_type
        SET task_state = '1_done'
        WHERE task_state = 'done'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task_type
        SET task_state = '1_canceled'
        WHERE task_state = 'cancelled'
        """,
    )
