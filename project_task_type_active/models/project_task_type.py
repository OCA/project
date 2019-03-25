# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProjectTaskType(models.Model):

    _inherit = 'project.task.type'

    active = fields.Boolean(default=True)
