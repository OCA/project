from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
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
