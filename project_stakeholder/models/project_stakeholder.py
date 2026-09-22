# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectStakeholder(models.Model):
    _name = "project.stakeholder"
    _description = "Project Stakeholder"

    role_id = fields.Many2one(
        "project.stakeholder.role",
        string="Stakeholder Role",
        required=True,
        ondelete="restrict",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Stakeholder",
        required=True,
        index=True,
        ondelete="cascade",
    )
    project_id = fields.Many2one(
        "project.project",
        required=True,
        index=True,
        ondelete="cascade",
    )
    note = fields.Text()
