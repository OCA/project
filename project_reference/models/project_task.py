# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    reference = fields.Char(string="Reference")
