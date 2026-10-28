# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def uninstall_hook(env):
    """Lift the visibility restrictions and restore the original group name."""
    # The restrictions and the 'group_full_project_manager' group are module data,
    # so they are removed on uninstall anyway. Archive the restrictions so that the
    # original administrator visibility is restored as soon as the hook runs.
    for xmlid in (
        "project_administrator_restricted_visibility.project_restricted_manager_rule",
        "project_administrator_restricted_visibility.task_restricted_manager_rule",
    ):
        if access := env.ref(xmlid, raise_if_not_found=False):
            access.active = False
    # Rename the 'Project: Administrator' access group back to 'Administrator'
    env.ref("project.group_project_manager").write({"name": "Administrator"})
