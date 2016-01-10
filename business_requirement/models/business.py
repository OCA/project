# -*- coding: utf-8 -*-
from openerp import api, fields, models


class BusinessRequirement(models.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "business.requirement"
    _description = "Business Requirement"

    sequence = fields.Char(
        'Sequence',
        readonly=True,
        copy=False,
        index=True,
    )
    name = fields.Char(
        'Name',
        required=False,
        readonly=True,
        copy=False,
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
        states={'draft': [('readonly', False)]},
        track_visibility='onchange'
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
        domain="[('id', '!=', id)]",
        readonly=True,
        states={'draft': [('readonly', False)]}
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
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        ondelete='set null',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    partner_id = fields.Many2one(
        related='project_id.partner_id',
        store=True,
        readonly=True,
    )
    sub_br_count = fields.Integer(
        string='Count',
        compute='_sub_br_count'
    )

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('business.requirement')
        return super(BusinessRequirement, self).create(vals)

    @api.multi
    @api.depends('parent_id')
    def _get_level(self):
        def _compute_level(br):
            return br.parent_id and br.parent_id.level + 1 or 1

        for br in self:
            level = _compute_level(br)
            br.level = level

    @api.one
    @api.depends('business_requirement_ids')
    def _sub_br_count(self):
        self.sub_br_count = len(self.business_requirement_ids)

    @api.model
    def _get_states(self):
        states = [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('approved', 'Approved'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
            ('drop', 'Drop'),
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

    @api.one
    def action_button_drop(self):
        self.write({'state': 'drop'})


class BusinessRequirementCategory(models.Model):
    _name = "business.requirement.category"
    _description = "Business Requirement Category"

    name = fields.Char(string='Name', required=True)
    parent_id = fields.Many2one(
        comodel_name='business.requirement.category',
        string='Parent Category',
        ondelete='restrict'
    )


class Project(models.Model):
    _inherit = "project.project"

    br_ids = fields.One2many(
        comodel_name='business.requirement',
        inverse_name='project_id',
        string='Business Requirement',
        copy=False,
    )
    br_count = fields.Integer(
        compute='_br_count',
        string="Business Requirement Number"
    )

    @api.one
    @api.depends('br_ids')
    def _br_count(self):
        self.br_count = len(self.br_ids)
