# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - 2015 Camptocamp
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
     'name': 'Projects Issue extensions',
    'version': '1.0',
    'category': 'Project Management',
    'summary': 'Add more filed',
    'description': """\
""",
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
        'project_issue_sheet',
        'hr_timesheet_sheet'
    ],
    'data': [
        'views/timesheet_view.xml',
        ],
    'installable': True,
}
