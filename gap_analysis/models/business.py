# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessEstimationLine(models.Model):
    _name = "business.estimation.line"
    _description = "Bus. Estimation Lines"

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name', required=True)
    business_requirement_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Business Analysis',
        ondelete='cascade'
    )
    type_id = fields.Many2one(
        comodel_name='business.estimation.type',
        string='Estimation Type',
        ondelete='restrict'
    )
    estimated_time = fields.Integer(string='Estimated Time', required=True)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assign To',
        ondelete='set null'
    )


class BusinessRequirement(models.Model):
    _name = "business.requirement"
    _description = "Business Analysis"

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
    draft_estimation_lines = fields.One2many(
        comodel_name='business.estimation.line',
        inverse_name='business_requirement_id',
        string='Draft Estimation Lines',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    categ_id = fields.Many2one(
        comodel_name='business.requirement.category',
        string='Category',
        ondelete='restrict',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    estimated_time_total = fields.Float(
        compute='_get_estimated_time_total',
        string='Total Estimated Time',
        store=True,
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
        string='Draft Estimation Lines',
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
    summary_estimation = fields.Boolean(
        string='Summary Estimation?',
        default=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='True: I will review the business case here.',
    )
    summary_estimation_note = fields.Text(
        'Summary Estimation Note',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('business.analysis')
        return super(BusinessRequirement, self).create(vals)

    @api.one
    @api.depends(
        'draft_estimation_lines.estimated_time')
    def _get_estimated_time_total(self):
        time_total = sum(
            line.estimated_time for line in self.draft_estimation_lines)
        self.estimated_time_total = time_total

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


class BusinessEstimationType(models.Model):
    _name = "business.estimation.type"
    _description = "Bus. Estimation Type"

    name = fields.Char(string='Name', required=True)
