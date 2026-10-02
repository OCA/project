# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    stakeholder_ids = fields.One2many(
        "project.stakeholder",
        "project_id",
        string="Stakeholders",
    )
