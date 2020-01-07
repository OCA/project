# -*- coding: utf-8 -*-
# Copyright 2020 Kmee Informática LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProjectProject(models.Model):

    _inherit = 'project.project'

    @api.multi
    def view_value_stream(self):
        self.ensure_one()
        action = self.env.ref(
            'project_wip.report_project_value_stream_act_window')
        action = action.read()[0]
        action['context'] = {
            'default_project_id': self.id
        }
        action['domain'] = [
            ('project_id', '=', self.id)
        ]
        return action
