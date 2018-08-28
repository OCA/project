from odoo import (
    api,
    fields,
    models,
    _
)

class Project(models.Model):
    _inherit = 'project.project'

    def _compute_sale_orders_count(self):
        for project in self:
            project.sale_order_count = self.env['sale.order'].search_count([
                ('related_project_id', '=', project.id)
            ])

    @api.multi
    def sale_order_tree_view(self):
        self.ensure_one()
        domain = [
            ('related_project_id', '=', self.ids)
        ]
        return {
            'name': _('Sale Orders'),
            'domain': domain,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                            Sale Orders can be related to your project.</p><p>
                            Go to your Sale Order and to click in the respective button 
                            to relate Sale Orders with your Project.
                        </p>'''),
            'limit': 80,
            'context': "{'default_related_project_id': '%s'}" % (self.id)
        }

    sale_order_count = fields.Integer(compute='_compute_sale_orders_count', string="Number of sale orders")
