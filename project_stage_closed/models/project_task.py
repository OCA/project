# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Task(models.Model):
    _inherit = 'project.task'

    closed = fields.Boolean(
        related='stage_id.closed',
        store=True,
    )
