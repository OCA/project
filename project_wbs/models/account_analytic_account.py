# Copyright 2017-19 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    _order = 'complete_wbs_code'

    @api.multi
    def get_child_accounts(self):
        result = {}
        if not self.ids:
            return result
        for curr_id in self.ids:
            result[curr_id] = True
        # Now add the children
        self.env.cr.execute('''
        WITH RECURSIVE children AS (
        SELECT parent_id, id
        FROM account_analytic_account
        WHERE parent_id IN %s
        UNION ALL
        SELECT a.parent_id, a.id
        FROM account_analytic_account a
        JOIN children b ON(a.parent_id = b.id)
        )
        SELECT * FROM children order by parent_id
        ''', (tuple(self.ids),))
        res = self.env.cr.fetchall()
        for x, y in res:
            result[y] = True
        return result

    @api.multi
    def write(self, vals):
        res = super(AccountAnalyticAccount, self).write(vals)
        if vals.get('parent_id'):
            for account in self.browse(self.get_child_accounts().keys()):
                account._complete_wbs_code_calc()
                account._complete_wbs_name_calc()
        if 'active' in vals:
            for account in self:
                account.project_ids.filtered(
                    lambda p: p.active != account.active).write(
                    {'active': account.active})
        return res

    @api.multi
    @api.depends('code')
    def _complete_wbs_code_calc(self):
        for account in self:
            data = []
            acc = account
            while acc:
                if acc.code:
                    data.insert(0, acc.code)

                acc = acc.parent_id
            if data:
                if len(data) >= 2:
                    data = ' / '.join(data)
                else:
                    data = data[0]
                data = '[' + data + ']'
            account.complete_wbs_code = data or ''

    @api.multi
    @api.depends('name')
    def _complete_wbs_name_calc(self):
        for account in self:
            data = []
            acc = account
            while acc:
                if acc.name:
                    data.insert(0, acc.name)
                acc = acc.parent_id
            if data:
                if len(data) >= 2:
                    data = ' / '.join(data)
                else:
                    data = data[0]
            account.complete_wbs_name = data or ''

    @api.multi
    def _wbs_indent_calc(self):
        for account in self:
            data = []
            acc = account
            while acc:
                if acc.name and acc.parent_id:
                    data.insert(0, '>')

                acc = acc.parent_id
            if data:
                if len(data) >= 2:
                    data = ''.join(data)  # pragma: no cover
                else:
                    data = data[0]
            account.wbs_indent = data or ''

    @api.multi
    @api.depends('account_class', 'parent_id')
    def _compute_project_analytic_id(self):
        for analytic in self:
            if analytic.parent_id:
                current = analytic.parent_id
            else:
                current = analytic
            while current.id:
                if current.account_class == 'project':
                    analytic.project_analytic_id = current
                    break
                current = current.parent_id

    @api.model
    def _default_parent(self):
        return self.env.context.get('parent_id', None)

    @api.model
    def _default_partner(self):
        return self.env.context.get('partner_id', None)

    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user)

    wbs_indent = fields.Char(
        compute=_wbs_indent_calc,
        string='Level'
    )

    complete_wbs_code = fields.Char(
        compute=_complete_wbs_code_calc,
        string='Full WBS Code',
        help='The full WBS code describes the full path of this component '
             'within the project WBS hierarchy',
        store=True,
    )
    code = fields.Char(copy=False)
    complete_wbs_name = fields.Char(
        compute=_complete_wbs_name_calc,
        string='Full WBS path',
        help='Full path in the WBS hierarchy',
        store=True
    )
    project_ids = fields.One2many(
        comodel_name='project.project',
        inverse_name='analytic_account_id',
        string='Projects',
    )
    project_analytic_id = fields.Many2one(
        'account.analytic.account',
        compute=_compute_project_analytic_id,
        string='Root Analytic Account',
        store=True
    )
    user_id = fields.Many2one(
        'res.users', 'Project Manager', track_visibility='onchange',
        default=_default_user)
    manager_id = fields.Many2one('res.users', 'Manager',
                                 track_visibility='onchange')

    account_class = fields.Selection(
        [('project', 'Project'), ('phase', 'Phase'),
         ('deliverable', 'Deliverable'),
         ('work_package', 'Work Package')], 'Class', default='project',
        help='The classification allows you to create a proper project '
             'Work Breakdown Structure'
    )
    parent_id = fields.Many2one(default=_default_parent,
                                string="Parent Analytic Account")
    partner_id = fields.Many2one(default=_default_partner)

    @api.multi
    def copy(self, default=None):
        if self.mapped('project_ids'):
            raise ValidationError(_('Duplicate the project instead of the '
                                    'Analytic Account'))
        default = {}
        default['code'] = self.env['ir.sequence'].next_by_code(
            'account.analytic.account.code')
        return super(AccountAnalyticAccount, self).copy(default)

    @api.multi
    @api.depends('code')
    def code_get(self):
        res = []
        for account in self:
            data = []
            acc = account
            while acc:
                if acc.code:
                    data.insert(0, acc.code)
                else:
                    data.insert(0, '')  # pragma: no cover

                acc = acc.parent_id
            data = ' / '.join(data)
            res.append((account.id, data))
        return res

    @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for account in self:
            data = []
            acc = account
            while acc:
                if acc.name:
                    data.insert(0, acc.name)
                else:
                    data.insert(0, '')  # pragma: no cover
                acc = acc.parent_id

            data = '/'.join(data)
            res2 = account.code_get()
            if res2 and res2[0][1]:
                data = '[' + res2[0][1] + '] ' + data

            res.append((account.id, data))
        return res

    _sql_constraints = [
        ('analytic_unique_wbs_code', 'UNIQUE (complete_wbs_code)',
         _('The full wbs code must be unique!')),
    ]
