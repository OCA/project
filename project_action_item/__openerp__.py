# -*- encoding: utf-8 -*-
##############################################################################
#
#    Project Action Item module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Project Action Item',
    'version': '0.1',
    'category': 'Project Management',
    'license': 'AGPL-3',
    'summary': 'Adds action items on tasks',
    'description': """
Project Action Item
===================

This module adds action items on project tasks. When a user has completed the action item of a task, he can click on a button *Done with Timesheet* that starts a wizard ; this wizard will mark the action item as done and will create a timesheet line.

This module depends on the module *hr_timesheet_task* which is available on http://code.launchpad.net/hr-timesheet.

Please contact Alexis de Lattre from Akretion <alexis.delattre@akretion.com> for any help or question about this module.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['project', 'hr_timesheet_task'],
    'data': [
        'wizard/update_action_generate_timesheet_view.xml',
        'project_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['project_demo.xml'],
    'images': [
        'static/src/img/screenshots/task_with_action_items.jpg',
        'static/src/img/screenshots/create_timesheet_from_action_item_wizard.jpg',
        ],
    'installable': True,
}
