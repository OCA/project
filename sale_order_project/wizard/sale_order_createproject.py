from odoo import api, fields, models, _


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

    sale_order_id = fields.Many2one('sale.order', string='Order', domain=[('type', '=', 'order')])
    related_project_id = fields.Many2one('project.project', string='Project')

    @api.multi
    def action_create_project_task(self):
        self.ensure_one()
        # get the lead to transform
        order = self.sale_order_id
        project = self.related_project_id

        # if related_project_id is empty
            # create new project.project
            return action_create_project(self)
        # else
            # update sales.order.related_project_id with the selected project.project.id
            vals = {
                'related_project_id': self.related_project_id,
            }
            order.write(vals)
            return True


