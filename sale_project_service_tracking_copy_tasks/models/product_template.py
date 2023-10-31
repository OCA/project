# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_tracking = fields.Selection(
        selection_add=[
            ("copy_tasks_in_project", "Copy tasks into sales order's project"),
        ],
    )
