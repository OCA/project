# © 2014 Akretion - Sébastien BEAU <sebastien.beau@akretion.com>
# © 2014 Akretion - Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.depends('analytic_account_id')
    def _compute_related_project_id(self):
        self.ensure_one()
        self.related_project_id = (
            self.env['project.project'].search(
                [('analytic_account_id', '=', self.analytic_account_id.id)],limit=1
            )[:1]
        )

    related_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        compute='_compute_related_project_id'
    )

    @api.model
    def _prepare_project_vals(self, order):
        name = "{0} - {1} - {2}".format(
            order.partner_id.name,
            date.today().year,
            order.name
        )
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
