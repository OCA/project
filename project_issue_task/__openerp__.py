# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
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
    'name': 'Project Issue related Tasks',
    'summary': 'Use Tasks to support Issue resolution reports',
    'version': '8.0.1.1.0',
    'category': 'Project Management',
    'description': """\
Support for the use case where solving an Issue means a Task should be done,
such as an on site visit, and a report must be made to document the work done.
This is a common scenario in technical field services.

The Issue form already has a "Task" field, allowing to create a Task related
to an Issue.
This module adds some usability improvements:

  * "Create Task" button on the Issue form
  * Automaticaly Close the Issue when the Task is Closed
  * Automatically Cancel the Task when Issue is Cancelled
  * Make the Task also visible to all followers of the related Issue
""",
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
        ],
    'data': [
        'project_issue_view.xml',
        'project_task_cause_view.xml',
        'project_task_view.xml',
        'security/ir.model.access.csv',
        'security/project_security.xml',
        ],
    'installable': True,
}
