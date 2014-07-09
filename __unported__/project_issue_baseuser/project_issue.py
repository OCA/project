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

from openerp.osv import orm


# Backport from trunk(v8) fix required. See Bug#1243628.
class ProjectIssue(orm.Model):
    _inherit = 'project.issue'

    def _get_default_partner(self, cr, uid, context=None):
        """
        If no other deafult is found, the current user is automatically
        added as the Contact for the issue.
        """
        res = super(ProjectIssue, self
                    )._get_default_partner(cr, uid, context=context)
        if not res:
            user = self.pool.get('res.users'
                                 ).browse(cr, uid, uid, context=context)
            res = user.partner_id and user.partner_id.id
        return res

    _defaults = {
        'partner_id': lambda s, cr, uid, c: s._get_default_partner(cr, uid, c),
    }
