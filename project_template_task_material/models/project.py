# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def copy(self, default=None):
        copy = super(ProjectTask, self).copy(default)
        if not self.project_id.is_template:
            # We do only copy if it is a template project
            return copy
        for material in self.material_ids:
            material.copy({'task_id': copy.id})
        return copy
