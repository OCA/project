# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    pg_model = env["procurement.group"]
    for task in env["project.task"].search([("move_ids", "!=", False)]):
        group = pg_model.create(task._prepare_procurement_group_vals())
        task.write({"group_id": group.id})
        task.move_ids.write({"group_id": group.id})
