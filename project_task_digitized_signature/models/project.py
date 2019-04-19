# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    customer_signature = fields.Binary(
        string='Customer acceptance',
    )

    @api.model
    def create(self, values):
        task = super(ProjectTask, self).create(values)
        if task.customer_signature:
            values = {'customer_signature': task.customer_signature}
            task._track_signature(values, 'customer_signature')
        return task

    @api.multi
    def write(self, values):
        self._track_signature(values, 'customer_signature')
        return super(ProjectTask, self).write(values)
