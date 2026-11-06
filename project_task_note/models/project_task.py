# Copyright 2024 Tecnativa Carolina Fernandez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    notes = fields.Html(string="Internal notes")
