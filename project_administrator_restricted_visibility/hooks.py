# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    """Restore project.project_project_manager_rule"""
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Removing the rule_groups of 'project.project_project_manager_rule'
    # from 'group_full_project_manager' group before removing the
    # 'group_full_project_manager' group in order to avoid getting
    # a SQL constraint error:
    # 'rule_group_rel_group_id_fkey'
    env.ref(
        "project_administrator_restricted_visibility.group_full_project_manager"
    ).write(
        {
            "rule_groups": [(3, env.ref("project.project_project_manager_rule").id)],
        }
    )

    # Removing the 'group_full_project_manager' group before renaming the original
    # 'Project: Full Administrator' group
    # (project.group_project_manager) to 'Administrator'
    # in order to avoid getting a SQL constraint error:
    # 'duplicate key value violates unique constraint "res_groups_name_uniq'"
    env.ref(
        "project_administrator_restricted_visibility.group_full_project_manager"
    ).unlink()

    # Rename the original 'Project: Full Administrator' access group back to 'Administrator'
    # and reassign the access rule for projects that it previously had.
    env.ref("project.group_project_manager").write(
        {
            "name": "Administrator",
            "rule_groups": [(4, env.ref("project.project_project_manager_rule").id)],
        }
    )
