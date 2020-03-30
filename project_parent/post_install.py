# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def restore_parents(cr, registry):
    # old reference to  analytic_account_id  on project table will be kept in
    # openupgrade_legacy_12_0_analytic_account_id column
    # NOTE we do not need to check for the existance of columns, because if
    # this is running project_project was surely installed in the previous
    # version.
    # on analytic_account_analytic we will have old field
    # openupgrade_legacy_12_0_parent_project_id we will now put it
    # check if openupgrade field exists (instance has been migrated using
    # openupgrade library)
    cr.execute(
        """
        SELECT count(attname)
        FROM pg_attribute
        WHERE attrelid = ( SELECT oid FROM pg_class WHERE relname = %s )
        AND attname = %s
        """,
        ('project_project', 'openupgrade_legacy_12_0_analytic_account_id')
    )
    if cr.fetchone()[0] == 1:
        cr.execute(
            """
            UPDATE project_project pp
            SET project_parent_id = aaa.parent_project_id
            FROM account_analytic_account aaa
            WHERE pp.openupgrade_legacy_12_0_analytic_account_id = aaa.id""",
        )
        return True
    # check if disregarded columns exist (instance has been previously migrated
    # using migration scripts without openupgrade)
    cr.execute(
        'SELECT count(attname) FROM pg_attribute '
        'WHERE attrelid = '
        '( SELECT oid FROM pg_class WHERE relname = %s ) '
        'AND attname = %s',
        ('account_analytic_account',
         'parent_project_id')
    )
    if cr.fetchone()[0] == 1:
        cr.execute(
            """
            UPDATE project_project pp
            SET project_parent_id = aaa.parent_project_id
            FROM account_analytic_account aaa
            WHERE pp.analytic_account_id = aaa.id""",
        )
        return True
