# -*- coding: utf-8 -*-
# Copyright 2017 Specialty Medical Drugstore
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"
    _name = "project.task"

    pr_uri = fields.Char(
        string='PR URI',
    )

    pr_required_states = fields.Many2many(
        related='project_id.pr_required_states',
    )

    @api.multi
    def write(self, vals, ):
        if vals.get('stage_id'):
            stage_id = vals.get('stage_id')
            num_states = len(self.project_id.pr_required_states)
            if self.pr_uri is False and num_states > 0:
                if (num_states >= 1 and
                        stage_id in
                        [state.id for state in
                         self.project_id.pr_required_states]):
                    raise exceptions.ValidationError(_(
                        'Please add the URI for the pull request '
                        'before moving the task to this stage.'
                    ))
        return super(ProjectTask, self).write(vals)
