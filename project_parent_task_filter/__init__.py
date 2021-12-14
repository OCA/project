from . import models

from odoo import api, SUPERUSER_ID


def _add_task_display_project(cr, registry):
    """This hook is used to set display_project_id field to the tasks that have a project_id set
     but empty display_project_id.
    This makes subtasks created in the Sub-task page of the parent Task visible in the project
     kanban view"""

    env = api.Environment(cr, SUPERUSER_ID, {})
    tasks = env["project.task"].search(
        [("parent_id", "!=", False), ("display_project_id", "=", False)]
    )
    for task in tasks:
        task.write({"display_project_id": task.parent_id.project_id.id})
