# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def post_init_hook(cr, registry):
    """Put the date with 00:00:00 as the date_time for the line."""
    cr.execute("""
        UPDATE account_analytic_line
        SET date_time = to_timestamp(date || ' 00:00:00',
                                     'YYYY/MM/DD HH24:MI:SS')
        """)
