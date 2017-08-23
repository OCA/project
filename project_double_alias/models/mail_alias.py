# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.html).

from odoo import api, models


class MailAlias(models.Model):
    _inherit = 'mail.alias'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get('alias_model_search'):
            model = self.env.context['alias_model_search']
            args.insert(0, ('alias_model_id.model', '=', model))
        return super(MailAlias, self).search(
            args, offset=offset, limit=limit, order=order, count=count,
        )
