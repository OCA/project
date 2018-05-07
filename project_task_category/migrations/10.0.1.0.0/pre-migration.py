# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr,
        'project_task',
        'categ_id'
    ) and not openupgrade.column_exists(
            env.cr,
            'project_task',
            openupgrade.get_legacy_name('categ_id')
    ):
            openupgrade.rename_columns(
                env.cr,
                {'project_task': [('categ_id', None)]})
