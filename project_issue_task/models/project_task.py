# -*- coding: utf-8 -*-
# Copyright 2015 - 2013 Daniel Reis
# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.multi
    @api.depends('issue_ids')
    def _compute_issue_id(self):
        for task in self:
            task.issue_id = task.issue_ids[:1]

    issue_id = fields.Many2one(
        comodel_name="project.issue", string="Main Issue",
        compute='_compute_issue_id', store=True,
    )
    issue_ids = fields.One2many(
        comodel_name='project.issue',
        inverse_name='task_id',
        string='Issues',
    )
    ref = fields.Char(string='Reference')
    reason_id = fields.Many2one(comodel_name='project.task.cause',
                                string='Problem Cause')

    @api.multi
    def write(self, values):
        """ On Task Close, also close Issue """
        res = super(ProjectTask, self).write(values)
        if 'stage_id' in values and self[:1].stage_id.fold:
            self.filtered('issue_ids').mapped('issue_ids').write({
                'stage_id': values.get('stage_id'),
            })
        return res
