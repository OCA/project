# -*- coding: utf-8 -*-
##############################################################################
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

from openerp import models, api


class project_task(models.Model):
    _inherit = 'project.task'

    @api.one
    @api.returns('project.task.type')
    def _get_state_stage(self, state_name):
        if self.project_id:
            stages = self.project_id.type_ids
            states = stages.filtered(lambda r: r.state == state_name)
        else:
            Stage = self.env['project.task.type']
            states = Stage.search([('state', '=', state_name)])
        if not states:
            raise Exception('No Stage for "%s" was found!' % state_name)
        return states[0]

    #
    # Keep button and case API from 7.0
    #

    @api.one
    def case_cancel(self):
        cancel_stage = self._get_state_stage('cancelled')
        self.stage_id = cancel_stage

    @api.one
    def do_cancel(self):
        self.case_cancel()

    @api.one
    def case_close(self):
        done_stage = self._get_state_stage('done')
        self.stage_id = done_stage

    @api.one
    def do_close(self):
        self.case_close()

    @api.one
    def action_close(self):
        self.case_close()
