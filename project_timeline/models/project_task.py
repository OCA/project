# -*- coding: utf-8 -*-
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.multi
    def onchange_user_id(self, user_id):  # pragma: no cover
        """Don't change date_start when changing the user_id. This screws up
        the default value passed by context when creating a record. It's also
        a nonsense to chain both values.
        """
        res = super(ProjectTask, self).onchange_user_id(user_id)
        if 'date_start' in res.get('value', {}):
            res['value'].pop('date_start')
        return res
