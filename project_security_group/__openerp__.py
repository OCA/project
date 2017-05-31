# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright 2013,2017 Daniel Reis <dreis.pt at hotmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Project Management Security Groups',
    'version': '9.0.2.0.0',
    'category': 'Project Management',
    'summary': 'Extend Project user roles to support more complex use cases',
    'author': "Daniel Reis, Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/project',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'project_stage_state',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/project_security.xml',
        ],
    'installable': True,
}
