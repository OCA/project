# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

def post_init_hook(env):
    env["project.task.type"].search([])._sync_task_stage_order()
