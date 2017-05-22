# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


_table_renames = [
    ('project_task_materials', 'project_task_material'),
]

_model_renames = [
    ('project.task.materials', 'project.task.material'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_models(env.cr, _model_renames)
