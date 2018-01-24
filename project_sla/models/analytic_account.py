# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    sla_ids = fields.Many2many('project.sla', string='Service Level Agreement')

    @api.multi
    def reapply_sla(self):
        """
        Force SLA recalculation on open documents that already are subject to
        this SLA Definition.
        To use after changing a Contract SLA or it's Definitions.
        """
        ctrl_obj = self.env['project.sla.control']
        for contract in self:
            # for each contract, and for each model under SLA control ...
            ctrl_models = set([sla.control_model for sla in contract.sla_ids])
            for model_name in ctrl_models:
                model = self.env[model_name]
                if 'analytic_account_id' in model._fields:
                    domain = [('analytic_account_id', '=', contract.id)]
                    docs = model.search(domain)
                if 'project_id' in model._fields:
                    domain = [
                        ('project_id.analytic_account_id', '=', contract.id)]
                    docs = model.search(domain)
                if docs:
                    ctrl_obj.store_sla_control(docs)
        return True
