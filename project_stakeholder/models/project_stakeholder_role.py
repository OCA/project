# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectStakeholderRole(models.Model):
    _name = "project.stakeholder.role"
    _description = "Project Stakeholder Role"
    _order = "name"

    name = fields.Char(string="Stakeholder Role", required=True, translate=True)
