# copyright 2020 Bogdan Stanciu <bogdanovidiu.stanciu@gmail.com>

from psycopg2.extensions import AsIs

from openupgradelib import openupgrade


def compute_codes_from_issues_fields(env):
    """If the OCA module `project_issue_code` was installed in the
    previous version, the `code` field for newly created tasks from issues
    will be empty, so we need to fill it in order to keep the uniqueness
    condition.
    """
    origin_issue_column = openupgrade.get_legacy_name('origin_issue_id')
    if not openupgrade.column_exists(env.cr, 'project_task',
                                     origin_issue_column):
        return
    env.cr.execute(
        """
        UPDATE project_task pt
            SET code=pi.issue_code
            FROM project_issue pi
            WHERE pt.%s=pi.id AND %s IS NOT NULL""",
        (AsIs(origin_issue_column), AsIs(origin_issue_column), )
        )


@openupgrade.migrate()
def migrate(env, version):
    compute_codes_from_issues_fields(env)
