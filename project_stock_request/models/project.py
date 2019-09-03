# Copyright (C) 2019 - TODAY, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    stock_request_order_ids = fields.One2many('stock.request.order',
                                              'project_id',
                                              string='Stock Request Orders')
