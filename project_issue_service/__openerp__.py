# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Daniel Reis
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
    'name': 'Project Issue and Task integration',
    'version': '1.1',
    'category': 'Project Management',
    'description': """\
Integrate Issues and Tasks in a common workflow, as is common in service management scenarios.

1. End user creates new Issue
2. Service Desk User reviews the new Issue:
    If a technical person intervention is needed, creates a Task for it.
    If not, it's closed without the need for an intervention Task.
3. Service Team User schedules the new Task
4. Service Team User completes the Task. The issue is automatically closed.

CHANGE LOG
============
1.1    Reference sequence (`ref` field) moved to module `project_issue_sequences`.

""",
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': [
        'project', 'project_functional_blocks',
        'project_issue',
        'project_issue_department',
        'project_issue_sequences',
        'crm_categ_hierarchy',
        'crm',
        ],
    'update_xml': [
        'project_issue_view.xml',
        'project_task_view.xml',
        'board_project_view.xml',
        #'project_issue_workflow.xml', #<= not using it, to avoid migrating former Issues to the new workflow
        ],
    'installable': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
