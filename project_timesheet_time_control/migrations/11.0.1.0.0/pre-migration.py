# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def move_date_time_from_issue(env):
    """Take the value of the field `date_time` from issues and set it on
    the tasks created from them.
    """
    origin_issue_column = openupgrade.get_legacy_name('origin_issue_id')
    openupgrade.logged_query(
        env.cr, """
        UPDATE project_task pt
        SET date_time = pi.date_time
        FROM project_issue pi
        WHERE pt.%s = pi.id""", (AsIs(origin_issue_column), ),
    )


@openupgrade.migrate()
def migrate(env, version):
    move_date_time_from_issue(env)
