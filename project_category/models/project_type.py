# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectType(models.Model):
    _name = 'project.type'
    _description = 'Project Type'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    description = fields.Text(
        translate=True,
    )
