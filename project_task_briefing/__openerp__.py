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
    'name': 'Project Task briefing information',
    'summary': 'Repurpose the task description field for task briefing'
               ' information',
    'version': '1.0',
    "category": "Project Management",
    'author': "Daniel Reis, Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/project-service',
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'project_task_view.xml',
    ],
    'installable': True,
}
