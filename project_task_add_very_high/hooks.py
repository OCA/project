# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def uninstall_hook(cr, registry):
    # convert priority from very high to high to avoid inconsistency
    # after the module is uninstalled
    cr.execute(
        "UPDATE project_task SET priority = '1' WHERE priority like '2'"
    )
