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

from openerp import models, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.onchange('analytic_account_id')
    def onchange_analytic(self):
        res = super(ProjectTask, self).onchange_analytic()
        warn = self.analytic_account_id.project_task_warn
        if warn and warn != 'no-message':
            warn_msg = {
                'title': _("Warning: %s") % (self.name or ''),
                'message': self.analytic_account_id.project_task_warn_msg}
            if warn == 'block':
                self.analytic_account_id = None
                self.partner_id = None
                self.location_id = None
            res = {'warning': warn_msg}
        return res
