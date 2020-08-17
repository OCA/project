# Copyright (C) 2020 - TODAY, Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, tools


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    ev_percent = fields.Integer('Earned Value %')
