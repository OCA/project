# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    task_dependency_arrange = fields.Boolean(
        string='Arrange tasks based on dependencies'
    )

    def set_values(self):
        self.env['ir.config_parameter'].set_param(
            'project_task_dependency.task_dependency_arrange',
            self.task_dependency_arrange
        )
        return super(ResConfigSettings, self).set_values()

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['task_dependency_arrange'] = \
            self.env['ir.config_parameter'].get_param(
                'project_task_dependency.task_dependency_arrange',
                False
            )
        return res
