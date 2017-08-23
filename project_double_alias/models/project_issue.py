# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.html).

from odoo import api, models


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.model
    def message_get_reply_to(self, res_ids, default=None):
        return super(
            ProjectIssue, self.with_context(alias_model_search=self._name),
        ).message_get_reply_to(res_ids, default=default)
