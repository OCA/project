# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def uninstall_hook(env):
    """Restore the original project administrator group name."""
    # The access restrictions and the 'group_full_project_manager' group are module
    # data, so they are removed on uninstall. Only the renamed 'Project:
    # Administrator' access group (project.group_project_manager) needs restoring.
    env.ref("project.group_project_manager").write({"name": "Administrator"})
