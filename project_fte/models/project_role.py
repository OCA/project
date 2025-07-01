from odoo import fields, models


class ProjectRole(models.Model):
    _inherit = "project.role"

    price_hour = fields.Float(
        string="Price per Hour",
        help="Price per hour for this role.",
        digits=(16, 2),
    )
