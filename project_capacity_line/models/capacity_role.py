# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CapacityRole(models.Model):
    _name = "capacity.role"
    _description = "Employee role for task matching"

    name = fields.Char(required=True)
    description = fields.Text()
