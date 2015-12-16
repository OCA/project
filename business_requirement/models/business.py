# -*- coding: utf-8 -*-
# © 2015 Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirement(models.Model):
    _name = "business.requirement"
    _description = "Business Requirement"

    sequence = fields.Char(
        'Sequence',
        readonly=True,
        copy=False,
    )
    name = fields.Char(
        'Name',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    description = fields.Char(
        'Description', required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    business_requirement = fields.Text(
        'Customer Story',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    scenario = fields.Text(
        'Scenario',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    gap = fields.Text(
        'Gap',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    drop = fields.Boolean(
        string='Drop?',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="""Determine whether this business requirement is to be kept
        or dropped."""
    )
    categ_id = fields.Many2one(
        comodel_name='business.requirement.category',
        string='Category',
        ondelete='restrict',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    state = fields.Selection(
        selection="_get_states",
        string='State',
        default='draft',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    business_requirement_ids = fields.One2many(
        comodel_name='business.requirement',
        inverse_name='parent_id',
        string='Sub Business Requirement',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    parent_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Parent',
        ondelete='set null',
        domain="[('id', '!=', id)]"
    )
    level = fields.Integer(
        compute='_get_level',
        string='Level',
        store=True
    )
    change_request = fields.Boolean(
        string='Change Request?',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('business.requirement')
        return super(BusinessRequirement, self).create(vals)

    @api.multi
    @api.depends(
        'parent_id')
    def _get_level(self):
        def _compute_level(br):
            level = 1
            if br.parent_id:
                level += _compute_level(br.parent_id)
            return level

        for br in self:
            level = _compute_level(br)
            br.level = level

    @api.model
    def _get_states(self):
        states = [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('approved', 'Approved'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ]
        return states

    @api.one
    def action_button_confirm(self):
        self.write({'state': 'confirmed'})

    @api.one
    def action_button_back_draft(self):
        self.write({'state': 'draft'})

    @api.one
    def action_button_approve(self):
        self.write({'state': 'approved'})

    @api.one
    def action_button_done(self):
        self.write({'state': 'done'})

    @api.one
    def action_button_cancel(self):
        self.write({'state': 'cancel'})


class BusinessRequirementCategory(models.Model):
    _name = "business.requirement.category"
    _description = "Business Requirement Category"

    name = fields.Char(string='Name', required=True)
    parent_id = fields.Many2one(
        comodel_name='business.requirement.category',
        string='Parent Category',
        ondelete='restrict'
    )
