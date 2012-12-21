# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Daniel Reis
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

from osv import fields, orm


class project_issue(orm.Model):
    _inherit = 'project.issue'
    _columns = {
        'regarding_uid': fields.many2one('res.users', 'Regarding User', help = "User affected by the Issue"),
    }
    _defaults = {
        'regarding_uid': lambda s, cr, uid, c: uid,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: