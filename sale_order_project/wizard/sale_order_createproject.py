from odoo import api, fields, models, _


class SaleOrderCreateProject(models.TransientModel):
    """ wizard to create a Project from a Sale Order """
    _name = "sale.order.createproject"

    @api.model
    def default_get(self, fields):
        result = super(SaleOrderCreateProject, self).default_get(fields)
        order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        if order:
            result.update({'sale_order_id': order.id})

    sale_order_id = fields.Many2one('sale.order', string='Order', domain=[('type', '=', 'order')])
    related_project_id = fields.Many2one('project.project', string='Project')

    @api.multi
    def action_create_project_task(self):
        self.ensure_one()
        # get the order to update
        order = self.sale_order_id
        project = self.related_project_id

        if project and not order.related_project_id:
        # if related_project_id is empty
            # create new project.project
            return order.action_create_project()
        else:
        # else
            # update sale.order.related_project_id with the selected project.project.id
            vals = {
                'related_project_id': self.related_project_id,
            }
            order.write(vals)
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target': 'new',
                'context': {'default_name': "Successfully Created."}
            }
