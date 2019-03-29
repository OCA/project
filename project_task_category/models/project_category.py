# © 2017-2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProjectCategory(models.Model):
    """Data Model for Project Category."""

    _name = 'project.category'
    _inherit = 'project.tags'

    description = fields.Char()
