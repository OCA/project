# Copyright 2019 KMEE INFORMÁTICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Task(models.Model):
    _inherit = "project.task"

    wip_ids = fields.One2many(
        comodel_name="project.wip",
        inverse_name="task_id",
        string="Project wip",
        required=False,
    )

    @api.model
    def create(self, vals):
        task = super(Task, self).create(vals)
        if task.active:
            task.wip_ids.start(task.id, task.stage_id.id)
        return task

    @api.multi
    def write(self, vals):
        if vals.get('stage_id'):
            self.wip_ids.stop()
            self.wip_ids.start(self.id, vals.get('stage_id'))
        if 'active' in vals:
            if not vals.get('active'):
                self.wip_ids.stop()
            else:
                self.wip_ids.start(self.id, vals.get('stage_id',
                                                     self.stage_id.id))
        return super(Task, self).write(vals)
