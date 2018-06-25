# -*- coding: utf-8 -*-
# © 2018 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(cr, 'project_category_main') and \
            openupgrade.table_exists(cr, 'project_category'):
        openupgrade.logging("Starting migrate project_category...")
        query = """
            INSERT INTO project_category
             (name, create_uid, create_date, write_uid, write_date)
            SELECT name, create_uid, create_date, write_uid, write_date
            FROM project_category_main
            WHERE NOT EXISTS
             (SELECT id FROM project_category
              WHERE project_category_main.name = project_category.name
             );
        """
        openupgrade.logged_query(cr, query)
        openupgrade.logging("Migrate project_category done.")
    else:
        openupgrade.logging("No need to be migrated.")
        return
