# -*- coding: utf-8 -*-
# Copyright (C) 2017 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.update_module_names(
        cr,
        [('service_desk_issue', 'project_contract_location_issue')],
    )
