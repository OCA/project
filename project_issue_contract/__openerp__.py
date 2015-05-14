# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012-2013 Daniel Reis
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
    'name': 'Contract on Project Issues',
    'summary': 'Add Contract and Location information to Issues',
    'version': '1.2',
    "category": "Project Management",
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
        'project_task_contract',
    ],
    'data': [
        'service_desk_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
