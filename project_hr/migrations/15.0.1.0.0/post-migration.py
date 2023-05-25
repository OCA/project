# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Convert m2o to m2m in 'project.task'
    openupgrade.m2o_to_x2m(
        env.cr,
        env["project.task"],
        "project_task",
        "employee_ids",
        "employee_id",
    )
