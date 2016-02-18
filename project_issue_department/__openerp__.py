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
{
    'name': 'Project Issue with Department',
    'version': '8.0.1.1.0',
    "category": "Project Management",
    'description': """\
Add Department field to Project Issues.

Selecting a Project for an issue will automatically populate this with the
Project's defined Department.
""",
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'daniel.reis@securitas.pt',
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
        'project_department',
    ],
    'data': [
        'project_issue_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
