# Copyright 2021 Open Source Integrators - Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def populate_date_start(cr, registry):
    """
    The date_start was introduced to be used instead of date_assign.
    To keep same behaviour on upgrade, initialize it
    to have the same data as before.
    """
    cr.execute(
        "UPDATE project_task "
        "SET date_start = date_assign "
        "WHERE date_start IS NULL "
        "AND date_assign IS NOT NULL"
    )
