# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2012
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
    'name': 'Project Issue - automatic responsible assignment',
    'version': '6.1',
    "category": "Project Management",
    'description': """
    Automatically assign a responsible when creating a new Issue, or other type of document. 
    Responsible person is looked up on a "profiling" table based on Sales Team and Department.
    "Sales Teams" allow to define different target teams. Originally are ment for Sales people, but here are (re)used also for Service Teams handling Issues, Claims, Tasks, etc.
    Initially was ment to on Issues, but currently it's generic enough to work on any object: crm.case, crm.claim, project.task, etc. 
    This module doesn't even require for Project to be installed. The names used are project related for historic reasons.
    
    Usage:
    - Profiling rules are defined either on Department form or on User form.
    - User is assigned by a Server Action. Example using Project Issues:
                Object:         project.issue.profiling
                Action Type:    Python Code
                Python Code:    self.set_user_id(cr, uid, [context.get('active_id')], 'project.issue', override_flds=['project_id.user_id'], context=context)
    - Server action can be called by an Automated Action or by a Workflow.
    """,
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': [
        'hr', #hr.department
        'crm', #case.section
    ],
    'init_xml': [],
    'update_xml': [
        'project_issue_profiling_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
