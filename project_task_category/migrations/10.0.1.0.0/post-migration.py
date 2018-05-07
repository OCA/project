# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


_old_new_table = (
    'project_category_main',
    'project_category')

_tables_affected = [
    ('project_task', 'categ_id')]


def get_set_task_category_id(env, old_categ_id):
    cr = env.cr
    old_table, new_table = _old_new_table
    # get name from the old table
    cr.execute("""
        SELECT id, name FROM %s
        WHERE id = %s
    """ % (old_table, old_categ_id))
    old_record = cr.fetchone()
    name = old_record[1]

    # check if already exist on the new table
    cr.execute("""
        SELECT id, name FROM %s
        WHERE name = '%s'
    """ % (new_table, name))

    new_record = cr.fetchone()
    # return id or create new one
    if new_record:
        return new_record[0]
    else:
        cr.execute("""
            INSERT INTO %s (name)
            VALUES ('%s')
            RETURNING id
        """ % (new_table, name))
        new_record = cr.fetchone()
        return new_record[0]


def migrate_task_category(env, table_affected):
    cr = env.cr
    table_name, field = table_affected
    if not openupgrade.column_exists(
            env.cr, table_name,
            openupgrade.get_legacy_name(field)):
        return
    legacy_name = openupgrade.get_legacy_name(field)

    cr.execute("""
        SELECT id, %s FROM %s
        WHERE %s IS NOT NULL
    """ % (legacy_name, table_name, legacy_name))
    records = cr.fetchall()
    for task_record in records:
        task_id, old_categ_id = task_record
        new_categ_id = get_set_task_category_id(
            env, old_categ_id)
        query = "UPDATE %s SET %s = %s WHERE id = %s" % (
            table_name, field, new_categ_id, task_id)
        openupgrade.logged_query(cr, query)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    for table_affected in _tables_affected:
        migrate_task_category(env, table_affected)
