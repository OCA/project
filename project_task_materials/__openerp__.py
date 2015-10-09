# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
#    Copyright (C) 2015 - Antiun Ingeniería S.L. - Sergio Teruel
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
    'summary': 'Record products spent in a Task',
    'version': '8.0.1.0.0',
    'category': "Project Management",
    'author': "Daniel Reis,"
              "Antiun Ingeniería S.L.,"
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'description': """\
Project Tasks allow to record time spent, but some activities, such as
Field Service, often require you to keep a record of the materials spent.

This module adds the ability to also this material spending.
To use it, make sure the "Log work activities on tasks" Project setting is
activated.

Note that only a simple record is made and no accounting or stock moves are
actually performed.""",
    'depends': ['project', 'product'],
    'data': [
        'views/project_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
