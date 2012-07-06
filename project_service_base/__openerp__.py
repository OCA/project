# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2012
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
    'name': 'Project & Service - base settings and security enhancements',
    'version': '6.1.1',
    "category": "Project Management",
    'description': """\
"Project" module renamed to "Project & Service".
Security levels:
    Project Basic User (new group): can create Issues and view Tasks.
    Project User: can edit Issues and create & edit Tasks.
    Project manager: can create and edit Projects.
""",
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': [
        'account', 
        'crm', 
        'project_issue', 
        'project_timesheet',
    ],
    'init_xml': [],
    'update_xml': [
        'project_view.xml',
        'security/project_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
