# Copyright 2019 KMEE INFORMÁTICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Task(models.Model):
    _inherit = "project.task"

    @api.model
    def create(self, vals):
        task = super(Task, self).create(vals)
        self.env['project.wip'].sudo().create({
            'project_id': task.project_id.id,
            'task_id': task.id,
            'task_stage_id': task.stage_id.name,
            'state': 'running',
        })
        return task

    @api.multi
    def write(self, vals):
        result = super(Task, self).write(vals)
        return result
