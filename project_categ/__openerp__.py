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
{
    'name': 'Project Configurable Categories',
    'summary': 'Allow for Project specific category lists for Tasks',
    'version': '8.0.0.1.1',
    "category": "Project Management",
    'description': """\
To setup:

  1. Create a parent Category (Tag). E.g. "System Type".
  2. Create categories to be made available as child.
     E.g. "Computer", "Printer", ...
  3. On the Project form, Other Info tab, set the "Root Category".

Now make this feature available on Issues or Tasks by installing the
corresponding extension module.
""",
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'depends': [
        'project',
        ],
    'data': [
        'project_categ_view.xml',
        ],
    'installable': True,
    'application': False,
}
