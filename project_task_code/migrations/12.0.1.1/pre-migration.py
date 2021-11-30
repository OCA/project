# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def uniqify_codes(env):
    """Gives all tasks of which the `code` field is not unique, a new
       (unique) value.
    """
    env.cr.execute("SELECT DISTINCT(code) FROM project_task")
    for row in env.cr.dictfetchall():
        task_code = row['code']
        code_is_null = not task_code or task_code == '/'

        if not code_is_null:
            env.cr.execute("SELECT id FROM project_task WHERE code = %s",
                [task_code])
        else:
            env.cr.execute("SELECT id FROM project_task "
                           "WHERE code IS NULL OR code = '/'")
        similar_task_ids = [x['id'] for x in env.cr.dictfetchall()]

        # Only change the tasks that are not the first of its kind and
        # not with code NULL.
        preserved_task_id = min(similar_task_ids) if not code_is_null else -1
        for similar_task_id in similar_task_ids:
            if similar_task_id > preserved_task_id:
                new_code = env['ir.sequence'].next_by_code('project.task')

                env.cr.execute(
                    "UPDATE project_task SET code = %s WHERE id = %s",
                    [new_code, similar_task_id]
                )


@openupgrade.migrate()
def migrate(env, version):
    uniqify_codes(env)
