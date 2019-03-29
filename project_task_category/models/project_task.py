# © 2017-2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Task(models.Model):
    """Inherit Project task to add category."""

    _inherit = 'project.task'

    categ_id = fields.Many2one(
        'project.category',
        'Category'
    )
