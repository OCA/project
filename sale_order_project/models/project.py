from odoo import (
    api,
    fields,
    models,
    _
)

class Project(models.Model):
    _inherit = 'project.project'

    sale_order_count = fields.Integer(compute='_compute_sale_orders_count', string="Number of sale orders")

    def _compute_sale_orders_count(self):
        SaleOrder = self.env['sale.order']
        for project in self:
            project.sale_order_count = SaleOrder.search_count([
                '&',
                ('res_model', '=', 'project.project'), ('res_id', '=', project.id),
            ])

