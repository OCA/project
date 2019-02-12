# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    cr.execute(
        """UPDATE account_analytic_line
        SET
            timetracker_started_at = date_time,
            timetracker_stopped_at = date_time + interval '1h' * unit_amount
        WHERE
            date_trunc('day', date_time) <> date_time;
        """
    )
