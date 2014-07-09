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
    'name': 'Per Project Configurable Categories',
    'summary': 'Projects can have an allowed category list',
    'version': '0.1',
    "category": "Project Management",
    'description': """\
To use:
  1. Create a parent Category (Tag). E.g. "System Type".
  2. Create categories to be made available as child. E.g. "Computer", "Printer", ...
  3. On the Project form, Other Info tab, set the "Root Category".

Now, Tasks for that Project will require you to set a Tag and it will only
be selectable from the Project's list.
""",
    'author': 'Daniel Reis',
    'depends': [
        'project',
        ],
    'data': [
        'project_categ_view.xml',
        ],
    'installable': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
