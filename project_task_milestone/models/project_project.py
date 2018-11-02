# Copyright 2018 Gontzal Gomez - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    plan_ids = fields.One2many(
        string='Phase Plan', comodel_name='project.task.plan',
        inverse_name='project_id', readonly=True)
