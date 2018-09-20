# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string="Employees",
    )
