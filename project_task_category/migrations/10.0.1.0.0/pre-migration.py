# -*- coding: utf-8 -*-
# © 2018 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

_logger = logging.getLogger(__name__)
try:
    from openupgradelib import openupgrade
except (ImportError, IOError) as err:
    _logger.debug(err)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    if not openupgrade.table_exists(cr, 'project_category_main') or \
            not openupgrade.table_exists(cr, 'project_category'):
        openupgrade.logging("No need to be migrated.")
        return
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

    update_categ_query = """
        UPDATE project_task task
        SET categ_id = categ.id
        FROM project_category categ, project_category_main categ_main
        WHERE categ.name = categ_main.name AND task.categ_id = categ_main.id;
    """
    openupgrade.logged_query(cr, update_categ_query)
    openupgrade.logging("Migrate project_category done.")
