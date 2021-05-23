import logging

logger = logging.getLogger(__name__)


def migrate(cr, _):
    logger.info(
        "Set project.task.type is_closed field using closed field if set "
        " and drop closed field"
    )
    cr.execute(
        """UPDATE project_task_type SET is_closed = closed
            WHERE closed is not NULL;
        """
        "ALTER TABLE project_task_type DROP COLUMN closed;"
    )
