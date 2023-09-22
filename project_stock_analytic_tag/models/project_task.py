# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    stock_analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        relation="account_analytic_tag_project_task_stock_rel",
        column1="project_task_id",
        column2="account_analytic_tag_id",
        string="Move Analytic Tags",
    )
