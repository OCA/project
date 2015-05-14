# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Daniel Reis
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
import logging
_logger = logging.getLogger(__name__)


class AnalyticAccount(orm.Model):
    """ Add SLA to Analytic Accounts """
    _inherit = 'account.analytic.account'
    _columns = {
        'sla_ids': fields.many2many(
            'project.sla', string='Service Level Agreement'),
        }

    def _reapply_sla(self, cr, uid, ids, recalc_closed=False, context=None):
        """
        Force SLA recalculation on open documents that already are subject to
        this SLA Definition.
        To use after changing a Contract SLA or it's Definitions.
        The ``recalc_closed`` flag allows to also recompute closed documents.
        """
        ctrl_obj = self.pool['project.sla.control']
        for contract in self.browse(cr, uid, ids, context=context):
            # for each contract, and for each model under SLA control ...
            ctrl_models = set([sla.control_model for sla in contract.sla_ids])
            for model_name in ctrl_models:
                model = self.pool[model_name]
                base = [] if recalc_closed else [('stage_id.fold', '=', 0)]
                doc_ids = []
                if 'analytic_account_id' in model._columns:
                    domain = base + [
                        ('analytic_account_id', '=', contract.id)]
                    doc_ids += model.search(cr, uid, domain, context=context)
                if 'project_id' in model._columns:
                    domain = base + [
                        ('project_id.analytic_account_id', '=', contract.id)]
                    doc_ids += model.search(cr, uid, domain, context=context)
                if doc_ids:
                    model = self.pool[model_name]
                    docs = model.browse(cr, uid, doc_ids, context=context)
                    ctrl_obj.store_sla_control(cr, uid, docs, context=context)
        return True

    def reapply_sla(self, cr, uid, ids, context=None):
        """ Reapply SLAs button action """
        return self._reapply_sla(cr, uid, ids, context=context)
