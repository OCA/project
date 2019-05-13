# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def add_product_with_specific_seniority_level(self, employee):
        """Add any product with a specific seniority level ot the order."""
        any_product = self.env['product.product'].search(
            [('seniority_level_id', '=', employee.seniority_level_id.id,)],
            limit=1,
        )
        if not any_product:
            raise UserError(_('No product exists with this seniority level.'))
        so_line = self.sudo().order_line.create({
            'order_id': self.id,
            'product_id': any_product.id,
            'product_uom_qty': 0,
        })
        so_line.alert_salesman_new_product(employee)
        return so_line


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    def alert_salesman_new_product(self, employee):
        self.env['mail.activity'].create({
            'res_id': self.order_id.id,
            'res_model_id': self.env.ref(
                'sale.model_sale_order').id,
            'activity_type_id': 4,
            'user_id': self.order_id.user_id.id,
            'summary': _('Please check the product {} for {}.').format(
                self.product_id.name, employee.name),
        })
