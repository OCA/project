# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class ProjectType(models.Model):
    _inherit = "project.type"

    timesheet_ok = fields.Boolean(string="Can be applied for timesheets")

