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
    'name': 'Project & Service - base settings and security enhancements',
    'version': '1.0',
    "category": "Project Management",
    'description': """\
"Project" module renamed to "Project & Service".

Standard security groups:
    User:     creates issues; reads tasks and projects; sees only own project's tasks.
    Manager:  writes issues, tasks and projects; can see all projects.

New security groups:
    Team Member: writes issues and tasks; reads projects; sees only own project's tasks.
""",
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': ['account', 'crm'],
    'init_xml': [],
    'update_xml': [
        'project_view.xml',
        'security/project_security.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
