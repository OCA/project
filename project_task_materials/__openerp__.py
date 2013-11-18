# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
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

{
    'name': 'Project Task Materials',
    'summary': 'Record products spend in a Task',
    'version': '1.0',
    'category': "Project Management",
    'author': 'Daniel Reis',
    'description': """\
Project Tasks allow to record time spent, if the "Log work activities on tasks"
setting is activated.
This nodules allows to also record materials spent, as is often needed in the
case of field service activities.

Important note: this implementation module does not integrate with stocks o
r accounting.""",
    'depends': ['project', 'product'],
    'data': [
        'project_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
