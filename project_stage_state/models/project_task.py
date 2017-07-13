# -*- coding: utf-8 -*-
# Copyright (C) 2013,2017 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import fields, models


_TASK_STATE = [
    ('draft', 'New'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled')]


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    state = fields.Selection(_TASK_STATE, 'State')


class ProjectTask(models.Model):
    _inherit = 'project.task'
    state = fields.Selection(
        related='stage_id.state', store=True, readonly=True)
