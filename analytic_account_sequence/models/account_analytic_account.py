# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#               <contact@eficent.com>
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

from openerp.osv import fields, osv


class account_analytic_account(osv.osv):

    _inherit = 'account.analytic.account'

    def _create_sequence(
        self, cr, uid, analytic_account_id, context=None
    ):
        ir_sequence_obj = self.pool.get('ir.sequence')
        account_sequence_obj = self.pool.get('analytic.account.sequence')
        ir_sequence_ids = ir_sequence_obj.search(
            cr, uid,
            [('code', '=', 'analytic.account.sequence')],
            context=context
        )
        vals = {}
        if ir_sequence_ids:
            ir_sequence_id = ir_sequence_ids[0]
            ir_sequence = ir_sequence_obj.browse(
                cr, uid,
                ir_sequence_id,
                context=context
            )

            vals = {
                'analytic_account_id': analytic_account_id,
                'name': ir_sequence.name,
                'code': ir_sequence.code,
                'implementation': 'no_gap',
                'active': ir_sequence.active,
                'prefix': ir_sequence.prefix,
                'suffix': ir_sequence.suffix,
                'number_next': 1,
                'number_increment': ir_sequence.number_increment,
                'padding': ir_sequence.padding,
                'company_id': (
                    ir_sequence.company_id and
                    ir_sequence.company_id.id or
                    False
                ),
            }

        return account_sequence_obj.create(cr, uid, vals, context=context)

    _columns = {
        'sequence_ids': fields.one2many(
            'analytic.account.sequence',
            'analytic_account_id',
            "Child code sequence"),
    }

    _defaults = {
        'code': False
    }

    def create(self, cr, uid, vals, *args, **kwargs):

        context = kwargs.get('context', {})
        # Assign a new code, from the parent account's sequence, if it exists.
        # If there's no parent, or the parent has no sequence, assign from the
        # basic sequence of the analytic account.
        new_code = False
        if 'parent_id' in vals and vals['parent_id']:
            account_obj = self.pool.get('account.analytic.account')
            obj_sequence = self.pool.get('analytic.account.sequence')
            parent = account_obj.browse(
                cr, uid,
                vals['parent_id'],
                context=context
            )
            if parent.sequence_ids:
                new_code = obj_sequence.next_by_id(
                    cr, uid,
                    parent.sequence_ids[0].id,
                    context=context
                )
            else:
                new_code = self.pool.get('ir.sequence').get(
                    cr, uid, 'account.analytic.account'
                )
        else:
            new_code = self.pool.get('ir.sequence').get(
                cr, uid, 'account.analytic.account'
            )

        if 'code' in vals and not vals['code'] and new_code:
            vals['code'] = new_code

        analytic_account_id = super(account_analytic_account, self).create(
            cr, uid, vals, *args, **kwargs
        )

        if 'sequence_ids' not in vals or (
            'sequence_ids' in vals and not vals['sequence_ids']
        ):
            sequence_id = self._create_sequence(
                cr, uid, analytic_account_id, context=context
            )
        return analytic_account_id

    def write(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}

        # If the parent project changes, obtain a new code according to the
        # new parent's sequence
        if 'parent_id' in data and data['parent_id']:
            obj_sequence = self.pool.get('analytic.account.sequence')
            parent = self.browse(cr, uid, data['parent_id'], context=context)
            if parent.sequence_ids:
                new_code = obj_sequence.next_by_id(
                    cr, uid, parent.sequence_ids[0].id, context=context
                )
                data.update({'code': new_code})

        return super(account_analytic_account, self).write(
            cr, uid, ids, data, context=context
        )

    def map_sequences(
        self, cr, uid,
        old_analytic_account_id, new_analytic_account_id,
        context=None
    ):
        """ copy and map tasks from old to new project """
        if context is None:
            context = {}
        map_sequence_id = {}
        sequence_obj = self.pool.get('analytic.account.sequence')
        account = self.browse(
            cr, uid, old_analytic_account_id, context=context
        )
        for sequence in account.sequence_ids:
            map_sequence_id[sequence.id] = sequence_obj.copy(
                cr, uid, sequence.id, {}, context=context
            )
        self.write(
            cr, uid,
            [new_analytic_account_id],
            {
                'sequence_ids': [
                    (6, 0, map_sequence_id.values())
                ]
            }
        )
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        default['sequence_ids'] = []
        res = super(account_analytic_account, self).copy(
            cr, uid, id, default, context
        )
        self.map_sequences(cr, uid, id, res, context)
        return res

account_analytic_account()
