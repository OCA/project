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
        sla_obj = self.pool.get('project.sla')

        context = {} if context is None else context.copy()

        exclude_states = ['cancelled', 'cancel']
        if not recalc_closed:
            exclude_states += ['done']

        # If this is called from SLA model, than we could reduce number of
        # documents that need recalculation
        if context.get('sla_ids', False):
            sla_ids = context['sla_ids']
        else:
            sla_ids = sla_obj.search(cr, uid, [('analytic_ids', 'in', ids)],
                                     context=context)

        sla_recs = sla_obj.browse(cr, uid, sla_ids, context=context)
        for m_name in set([sla.control_model for sla in sla_recs]):
            # for each contract, and for each model under SLA control ...
            model = self.pool.get(m_name)
            domain = [('state', 'not in', exclude_states)]

            # if model have both 'project_id' and 'analytic_account_id' fields,
            # then we should use `OR` condition to search for both of these
            # fields. Otherwise, search only by one of fields
            if ('analytic_account_id' in model._columns and
                    'project_id' in model._columns):
                domain += ['|', ('analytic_account_id', 'in', ids),
                                ('project_id.analytic_account_id', 'in', ids)]
            elif 'analytic_account_id' in model._columns:
                domain += [('analytic_account_id', 'in', ids)]
            elif 'project_id' in model._columns:
                domain += [('project_id.analytic_account_id', 'in', ids)]

            doc_ids = model.search(cr, uid, domain, context=context)

            if doc_ids:
                docs = model.browse(cr, uid, doc_ids, context=context)
                ctrl_obj.store_sla_control(cr, uid, docs, context=context)
        return True

    def reapply_sla(self, cr, uid, ids, context=None):
        """ Reapply SLAs button action """
        return self._reapply_sla(cr, uid, ids, context=context)
