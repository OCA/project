# © 2014 Akretion - Sébastien BEAU <sebastien.beau@akretion.com>
# © 2014 Akretion - Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


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
