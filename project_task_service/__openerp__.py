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
    'name': 'Project Task Record',
    'version': '1.0',
    "category": "Project Management",
    'description': """\
Add to project tasks all necessary fields to record a service intervention:
* Time spent
* Materials used
* Work done description
* Work pending description
* Problem cause identification

Before creating new Projects, review the following configurations::
* Stages: the task stages ""common to all projects" are assigned to new projects by default.
* Causes: the possible reasons for problem causing a service incidents.
* Functional Blocks: the sub-components or sub-systems for projects.

Contributions are appreciated. Some ideas to develop:
* add a 'crm_category_stages' module, to make configurable the stages (type_ids) valid for each Category.  
""",
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': ['project', 'project_functional_blocks', 'project_department'],
    'update_xml': [
        'project_task_cause_view.xml',
        'project_task_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
