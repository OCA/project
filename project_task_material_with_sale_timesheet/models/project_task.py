# Copyright 2019 Praxya - Juan Carlos Montoya
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class ProjectTaskMaterial(models.Model):
    _inherit = "project.task.material"

    @api.multi
    def create_analytic_line(self):
        return super(ProjectTaskMaterial, self.with_context(
            norecompute_amount=True
        )).create_analytic_line()
