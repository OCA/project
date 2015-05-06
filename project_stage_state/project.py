# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Daniel Reis
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


_TASK_STATE = [
    ('draft', 'New'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled')]


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    state = fields.Selection(_TASK_STATE, 'State')
    fold_statusbar = fields.Boolean('Folded in Statusbar')

    @api.model
    def _init_fold_statusbar(self):
        """ On module install initialize fold_statusbar values """
        for rec in self.search([]):
            rec.fold_statusbar = rec.fold


class ProjectTask(models.Model):
    _inherit = 'project.task'
    state = fields.Selection(
        related='stage_id.state', store=True, readonly=True)
