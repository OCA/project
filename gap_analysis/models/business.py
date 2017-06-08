# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <AUTHOR(Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
from openerp.osv import osv


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

    @api.model
    def _get_sequence(self):
        sequence = self.env['ir.sequence'].get('business.requirement')
        return sequence

    sequence = fields.Char(
        'Sequence',
        readonly=True,
        copy=False,
    )
    name = fields.Char(
        'Name', required=True,
        default=_get_sequence,
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
    odoo_scenario = fields.Text(
        'Odoo Scenario',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    odoo_gap = fields.Text(
        'Odoo Gap',
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
    rough_estimation_lines = fields.One2many(
        comodel_name='business.estimation.line',
        inverse_name='business_requirement_id',
        string='Rough Estimation Lines',
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
        string='Rough Estimation Lines',
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
        states={'draft': [('readonly', False)]}
    )
    summary_estimation_note = fields.Text(
        'Summary Estimation Note',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    @api.one
    @api.depends(
        'rough_estimation_lines.estimated_time')
    def _get_estimated_time_total(self):
        time_total = 0
        for line in self.rough_estimation_lines:
            time_total += line.estimated_time
        self.estimated_time_total = time_total

    @api.multi
    @api.depends(
        'parent_id')
    def _get_level(self):
        for br in self:
            level = br._compute_level()
            br.level = level

    @api.multi
    def _compute_level(self):
        level = 1
        if self.parent_id:
            level += self.parent_id._compute_level()
        return level

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
    _description = "Bus. Req. Category"

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
