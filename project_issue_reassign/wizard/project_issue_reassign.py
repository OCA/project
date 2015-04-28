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

from openerp import models, fields, api


class project_issue_reassign(models.TransientModel):
    _name = 'project.issue.reassign'
    _description = 'Issue Reassign'

    project_id = fields.Many2one(
        'project.project', 'Project',
        help="Project this issue should belong to")
    user_id = fields.Many2one(
        'res.users', 'Assign To',
        help="User you want to assign this issue to")

    @api.multi
    def reassign(self):
        active_ids = self.env.context['active_ids']
        issues = self.env['project.issue'].browse(active_ids)
        res = issues.do_reassign(self.user_id.id, self.project_id.id)
        return res
