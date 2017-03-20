# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    # convert priority to avoid inconsistency
    cr.execute(
        "UPDATE project_task SET priority = '2' WHERE priority like '3'"
    )
