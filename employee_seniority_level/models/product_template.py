# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    seniority_level_id = fields.Many2one(
        name='Seniority level',
        comodel_name='hr.employee.seniority.level',
        ondelete='restrict',
    )

    @api.onchange('type', 'service_policy')
    def onchange_type_service_policy(self):
        if (
            self.type != 'service'
            or self.service_policy != 'delivered_timesheet'
        ):
            self.seniority_level_id = None
