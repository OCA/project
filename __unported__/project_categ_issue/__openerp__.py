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
    'name': 'Per Project Configurable Categorie on Issues',
    'summary': 'Projects Issues can have an allowed category list',
    'version': '0.1',
    "category": "Project Management",
    'description': """\
Adds to Issues the ability to limit selectable Categories to a Proeject's
specific list.
""",
    'author': 'Daniel Reis',
    'depends': [
        'project_issue',
        'project_categ',
        ],
    'data': [
        'project_categ_view.xml',
        ],
    'installable': False,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
