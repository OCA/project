from odoo import api, fields, models, _

class SaleOrderCreateProject(models.TransientModel):
    """ wizard to create a Project from a Sale Order """
    _name = "sale.order.createproject"

    @api.model
    def default_get(self, fields):
        result = super(SaleOrderCreateProject, self).default_get(fields)
        sale_order_id = self.env.context.get('active_id')
        if sale_order_id:
            result['sale_order_id'] = sale_order_id
        return result

    sale_order_id = fields.Many2one('sale.order', string='Order', domain=[('type', '=', 'order')])
    related_project_id = fields.Many2one(
        'project.project',
        string='Project',
        help=_("Leave it blank if you want create a new project with the sale order's name as default name.")
    )

    @api.multi
    def action_create_project_task(self):
        self.ensure_one()
        # get the order to update
        order = self.sale_order_id
        project = self.related_project_id

        # if related_project_id is empty
        if not project.id and not order.related_project_id:
            # create new project.project
            order.action_create_project()
        # if project but order is not related to that project
        elif project.id and not order.related_project_id:
            # update sale.order.related_project_id with the selected project.project.id
            order.write({
                'analytic_account_id': project.analytic_account_id.id
            })
        # else
        else:
            raise Warning(_(
                'This sale order already has a related project. Order: {0}, Project: {1}'.format(order, order.related_project_id)
            ))

        return True
