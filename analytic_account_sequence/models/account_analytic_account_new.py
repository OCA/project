# -*- coding: utf-8 -*-
# © 2015 Eficent S.L. - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# © 2016 Matmoz d.o.o. - Matjaz Mozetic
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    @api.model
    def _create_sequence(self, analytic_account_id):
        ir_sequence_obj = self.env['ir.sequence']
        account_sequence_obj = self.env['analytic.account.sequence']
        ir_sequence_ids = ir_sequence_obj.search(
            [('code', '=', 'analytic.account.sequence')]
        )
        vals = {}
        if ir_sequence_ids:
            ir_sequence_id = ir_sequence_ids[0]
            ir_sequence = ir_sequence_obj.browse(ir_sequence_id)
            vals = {
                'analytic_account_id': self.id,
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
        return account_sequence_obj.create(vals)

    sequence_ids = fields.One2many(
        'analytic.account.sequence',
        'analytic_account_id',
        "Child code sequence"
    )

    _defaults = {
        'code': False
    }

    @api.model
    def create(self, vals):
        # Assign a new code, from the parent account's sequence, if it exists.
        # If there's no parent, or the parent has no sequence, assign from
        # the basic sequence of the analytic account.
        new_code = False
        if 'parent_id' in vals and vals['parent_id']:
            account_obj = self.env['account.analytic.account']
            obj_sequence = self.env['analytic.account.sequence']
            parent = account_obj.browse(vals['parent_id'])
            if parent.sequence_ids:
                new_code = obj_sequence.next_by_id(parent.sequence_ids[0].id)
            else:
                new_code = self.env['ir.sequence'].\
                    get('account.analytic.account')
        else:
            new_code = self.env['ir.sequence'].get('account.analytic.account')
        if 'code' in vals and not vals['code'] and new_code:
            vals['code'] = new_code
        analytic_account = super(AccountAnalyticAccount, self).create(vals)
        if 'sequence_ids' not in vals or\
                ('sequence_ids' in vals and not vals['sequence_ids']):
            analytic_account._create_sequence()
        return analytic_account

    @api.multi
    def write(self, data):
        # If the parent project changes, obtain a new code according to the
        # new parent's sequence
        if 'parent_id' in data and data['parent_id']:
            obj_sequence = self.env['analytic.account.sequence']
            parent = self.browse(data['parent_id'])
            if parent.sequence_ids:
                new_code = obj_sequence.next_by_id(parent.sequence_ids[0].id)
                data.update({'code': new_code})
        return super(AccountAnalyticAccount, self).write(data)

    @api.model
    def map_sequences(self, new_analytic_account):
        """ copy and map tasks from old to new project """
        map_sequence_id = {}
        account = self
        for sequence in account.sequence_ids:
            map_sequence_id[sequence.id] = sequence.copy({}).id
        new_analytic_account.\
            write({'sequence_ids': [(6, 0, map_sequence_id.values())]})
        return True

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['sequence_ids'] = []
        res = super(AccountAnalyticAccount, self).copy(default)
        self.map_sequences(res)
        return res
