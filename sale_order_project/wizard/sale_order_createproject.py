from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import Warning


class SaleOrderCreateProject(models.TransientModel):
    """ wizard to create a Project from a Sale Order """
    _name = "sales.order.createproject"

    @api.model
    def default_get(self, fields):
        result = super(SaleOrderCreateProject, self).default_get(fields)
        sale_order_id = self.env.context.get('active_id')
        if sale_order_id:
            result['sale_order_id'] = sale_order_id
        return result

    sale_order_id = fields.Many2one('crm.lead', string='Lead', domain=[('type', '=', 'lead')])
    related_project_id = fields.Many2one('project.project', string='Project')


