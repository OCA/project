# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
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
<<<<<<< ff33f76c66d1cedc6dbd60cdf85ad0855da08321
    "name": "Work Breakdown Structure - Tasks",
    "version": "2.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Generic Modules/Projects & Services",
    "depends": ["project_wbs"],
    "description": """
Work Breakdown Structure - Tasks
================================
This module extends the standard Odoo functionality by adding:

- A button in the project tree view that will conduct the user to the list
view for the associated tasks.
- The possibility to search for task by the WBS complete reference or name.

    """,
    "data": [
        "view/project_task_view.xml",
        "view/project_view.xml",
=======
    'name': 'Work Breakdown Structure - Tasks',
    'version': '8.0.2.0.0',
    'author':   'Eficent, '
                'Matmoz d.o.o., '
                'Project Expert Team',
    'contributors': [
        'Jordi Ballester <jordi.ballester@eficent.com>',
        'Matjaž Mozetič <m.mozetic@matmoz.si>',
    ],
    'website': 'http://project.expert',
    'category': 'Project Management',
    'license': 'AGPL-3',
    'depends': ['project_wbs'],
    'data': [
        'view/project_task_view.xml',
        'view/project_view.xml',
>>>>>>> Enhance the module descriptions
    ],
    'demo': [

    ],
    'test': [
    ],
    'installable': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
