# -*- coding: utf-8 -*-
##############################################################################
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
    'name': 'Project Task Action Buttons',
    'summary': 'Add a Action Buttons on Task Form.',
    'version': '1.0',
    'category': 'Project Management',
    'author': 'Daniel Reis, Odoo Community Association (OCA)',
    'depends': [
        'project_stage_state'
        ],
    'data': [
        'project_task_view.xml',
        ],
    'installable': True,
}
