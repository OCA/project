# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "project.project",
                "project_project",
                "limit_timesheet_role_to_assignments",
                "limit_role_to_assignments",
            ),
            (
                "res.company",
                "res_company",
                "limit_timesheet_role_to_assignments",
                "project_limit_role_to_assignments",
            ),
        ],
    )
