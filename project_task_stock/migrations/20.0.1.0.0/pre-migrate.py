from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Rename project.task.group_id (procurement.group) to reference_id (stock.reference)
    openupgrade.rename_fields(
        env, [("project.task", "project_task", "group_id", "reference_id")]
    )
    # Migrate task_id from stock.scrap to stock.move
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE stock_move AS m
            SET task_id = s.task_id
            FROM stock_scrap AS s
            WHERE m.scrap_id = s.id AND s.task_id IS NOT NULL AND m.is_scrap IS TRUE
        """,
    )
