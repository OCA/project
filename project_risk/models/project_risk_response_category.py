# Copyright 2019 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProjectRiskResponseCategory(models.Model):
    _name = 'project.risk.response.category'

    name = fields.Char(required=True)
