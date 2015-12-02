# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    deliverable_lines = fields.One2many(
        comodel_name='business.deliverable.line',
        inverse_name='business_requirement_id',
        string='Deliverable Lines',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    estimated_time_total = fields.Float(
        compute='_get_estimated_time_total',
        string='Total Estimated Time',
        store=True,
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

    @api.one
    @api.depends(
        'deliverable_lines.estimated_time')
    def _get_estimated_time_total(self):
        time_total = sum(
            line.estimated_time for line in self.deliverable_lines
            if line.resouce_type == 'time')
        self.estimated_time_total = time_total


class BusinessDeliverableLine(models.Model):
    _name = "business.deliverable.line"
    _description = "Bus. Deliverable Lines"

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name', required=True)
    business_requirement_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Business Requirement',
        ondelete='cascade'
    )
    type_id = fields.Many2one(
        comodel_name='business.deliverable.type',
        string='Deliverable Type',
        ondelete='restrict'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assign To',
        ondelete='set null'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='UoM',
        required=True
    )
    qty = fields.Integer(
        string='Quantity'
    )
    estimated_time = fields.Integer(
        string='Estimated Time'
    )
    resouce_type = fields.Selection(
        selection=[('resource', 'Resource'), ('time', 'Time')],
        string='Resouce Type',
        default='time',
        required=True
    )

    @api.one
    @api.onchange('resouce_type')
    def resouce_type_change(self):
        if self.resouce_type == "resource":
            self.estimated_time = 0
        elif self.resouce_type == "time":
            self.qty = 0

    @api.one
    def write(self, vals):
        resouce_type = vals.get('resouce_type', False)
        if resouce_type == "resource":
            vals.update({'estimated_time': 0})
        elif resouce_type == "time":
            vals.update({'qty': 0})
        return super(BusinessDeliverableLine, self).write(vals)


class BusinessDeliverableType(models.Model):
    _name = "business.deliverable.type"
    _description = "Bus. Deliverable Type"

    name = fields.Char(string='Name', required=True)
