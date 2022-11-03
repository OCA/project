# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    type_id = fields.Many2one(
        comodel_name="project.type",
        string="Type",
        copy=False,
        domain="[('project_ok', '=', True)]",
    )
    type_color = fields.Integer(string="Type Color Index", related="type_id.color")
