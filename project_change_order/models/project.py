# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class Project(models.Model):
    _inherit = 'project.project'

    ref = fields.Char(string="Internal Reference")
    change_order_ids = fields.One2many('project.change_order', 'project_id')

    @api.multi
    def action_create_change_order(self):
        action = self.env.ref('project_change_order.change_order_action')
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_project_id': self.id,
            'default_ref': self.ref,
            'default_budget_id': self.budget_id.id,
        }
        res = self.env.ref('project_change_order.project_change_order_view_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        return result
