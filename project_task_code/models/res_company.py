# Copyright 2023 Abraham Anes <abrahamanes@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    project_task_seq_id = fields.Many2one(
        string="Project task sequence",
        comodel_name="ir.sequence",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
