# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Daniel Reis
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


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    def do_reassign(self, user=None, proj=None):
        """ Reassign an Issue to another User and/or Project """
        assert user or proj, _("No reassignment data was provided.")
        # write reassignment changes
        reassign_data = {}
        if user:
            reassign_data['user_id'] = user
        if proj:
            reassign_data['project_id'] = proj
        return self.write(reassign_data)
