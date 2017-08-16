# -*- coding: utf-8 -*-
# Copyright 2004-2010 Tiny SPRL <http://tiny.be>.
# Copyright 2017 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTimeboxFill(models.TransientModel):
    _name = 'project.timebox.fill.plan'
    _description = 'Project Timebox Fill'

    @api.model
    def _get_from_tb(self):
        timeboxes = self.env['project.gtd.timebox'].search([])
        return timeboxes and timeboxes[0] or False

    @api.model
    def _get_to_tb(self):
        return self.env.context.get('active_id')

    timebox_id = fields.Many2one(
        'project.gtd.timebox', 'Get from Timebox', required=True,
        default=_get_from_tb)
    timebox_to_id = fields.Many2one(
        'project.gtd.timebox', 'Set to Timebox', required=True,
        default=_get_to_tb)
    task_ids = fields.Many2many(
        'project.task',
        'project_task_rel', 'task_id', 'fill_id',
        'Tasks selection')

    @api.multi
    def process(self):
        self.ensure_one()
        if not self.task_ids:
            return {}
        self.task_ids.write({'timebox_id': self.timebox_to_id.id})
        return {'type': 'ir.actions.act_window_close'}
