def migrate(cr, _):
    cr.execute(
        """UPDATE project_task_type SET is_closed = closed
            WHERE closed is not NULL;
        """
    )
