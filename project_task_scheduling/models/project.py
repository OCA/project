# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Task(models.Model):
    _inherit = 'project.task'

    closed = fields.Boolean(
        related='stage_id.closed',
        store=True,
    )
