# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from openerp.addons.project_timesheet_time_control import post_init_hook


def migrate(cr, version):
    """Fill correct date time also on migrations from module
    project_work_time_control.
    """
    if not version:
        return
    post_init_hook(cr, None)
