# Copyright (C) 2019 Pavlov Media
# License Proprietary. Do not copy, share nor distribute.

from odoo import api, fields, models


class ChangeOrder(models.Model):
    _name = "project.change_order"
    _description = 'Change Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date'

    name = fields.Char(required=True)
    description = fields.Text()
    design = fields.Text()
    stage_id = fields.Many2one('project.change_order_stage',
                               string="Stage",
                               default=lambda self: self._default_stage_id())
    ref = fields.Char(string="Internal Reference")
    project_id = fields.Many2one('project.project', string="Project")
    currency_id = fields.Many2one('res.currency',
                                  string="Currency",
                                  related="project_id.currency_id")
    budget_id = fields.Many2one('crossovered.budget', string="Budget")
    change_order_line_ids = fields.One2many('project.change_order_line',
                                            'change_order_id',
                                            string="Budget Lines")
    total_change = fields.Float(string="Total Change",
                                compute="_line_total")

    def _default_stage_id(self):
        return self.env.ref(
            'project_budget_change_order.change_order_stage_draft')

    @api.depends('change_order_line_ids.change_value')
    def _line_total(self):
        for record in self:
            total_change = 0.0
            for line in record.change_order_line_ids:
                total_change += line.change_value
            record['total_change'] = total_change

    @api.multi
    def action_review(self):
        return self.write({'stage_id': self.env.ref(
            'project_budget_change_order.change_order_stage_review').id})

    @api.multi
    def action_draft(self):
        return self.write({'stage_id': self.env.ref(
            'project_budget_change_order.change_order_stage_draft').id})

    @api.multi
    def action_approve(self):
        for record in self:
            for change_line in record.change_order_line_ids:
                change_line.budget_line_id.planned_amount += \
                    change_line.change_value
            return record.write({'stage_id': self.env.ref(
                'project_budget_change_order.change_order_stage_approved').id})

    @api.multi
    def action_cancel(self):
        for record in self:
            for change_line in record.change_order_line_ids:
                change_line.budget_line_id.planned_amount -= \
                    change_line.change_value
            return record.write({'stage_id': self.env.ref(
                'project_budget_change_order.change_order_stage_canceled').id})

    @api.multi
    def action_view_order(self):
        self.ensure_one()
        action = self.env.ref(
            'project_budget_change_order.change_order_action').\
            read()[0]
        order = self.env['project.change_order'].search([('id', '=', self.id)])
        action['views'] = [(self.env.ref('project_budget_change_order.' +
                            'project_change_order_view_form').id, 'form')]
        action['res_id'] = order.id
        return action
