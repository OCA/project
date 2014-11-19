# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Vincent Renaville
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
    'name': 'Project Issue relate block hours',
    'summary': 'Print Ticket linked to project concerned by block hours',
    'version': '1.1',
    'category': 'Project Management',
    'description': """
Report on Project Issue linked to a project set in invoice line of the related block hours
""",
    'author': 'Vincent Renaville',
    'depends': [
        'project_issue',
        'analytic_hours_block'
        ],
    'data': [
             'data/header.xml',
             'report.xml',
        ],
    'installable': True,
}
