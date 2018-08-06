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

    @api.model
    def _prepare_project_vals(self, order):
        name = "%s - %s - %s" % (
            order.partner_id.name,
            date.today().year,
            order.name)
        return {
            'user_id': order.user_id.id,
            'name': name,
            'partner_id': order.partner_id.id,
        }

    @api.multi
    def action_create_project(self):
        project_obj = self.env['project.project']
        for order in self:
            if order.related_project_id:
                raise Warning(_(
                    'There is a project already related with this sale order.'
                ))
            vals = self._prepare_project_vals(order)
            project = project_obj.create(vals)
            order.write({
                'analytic_account_id': project.analytic_account_id.id
            })
        return True
