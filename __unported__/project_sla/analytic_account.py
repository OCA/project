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
        ctrl_obj = self.pool.get('project.sla.control')
        proj_obj = self.pool.get('project.project')
        exclude_states = ['cancelled'] + (not recalc_closed and ['done'] or [])
        for contract in self.browse(cr, uid, ids, context=context):
            # for each contract, and for each model under SLA control ...
            for m_name in set([sla.control_model for sla in contract.sla_ids]):
                model = self.pool.get(m_name)
                doc_ids = []
                if 'analytic_account_id' in model._columns:
                    doc_ids += model.search(
                        cr, uid,
                        [('analytic_account_id', '=', contract.id),
                         ('state', 'not in', exclude_states)],
                        context=context)
                if 'project_id' in model._columns:
                    proj_ids = proj_obj.search(
                        cr, uid, [('analytic_account_id', '=', contract.id)],
                        context=context)
                    doc_ids += model.search(
                        cr, uid,
                        [('project_id', 'in', proj_ids),
                         ('state', 'not in', exclude_states)],
                        context=context)
                if doc_ids:
                    docs = model.browse(cr, uid, doc_ids, context=context)
                    ctrl_obj.store_sla_control(cr, uid, docs, context=context)
        return True

    def reapply_sla(self, cr, uid, ids, context=None):
        """ Reapply SLAs button action """
        return self._reapply_sla(cr, uid, ids, context=context)
