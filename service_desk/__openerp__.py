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
    'name': 'Service Desk Central',
    'version': '0.1',
    "category": "Project Management",
    'description': """\
Concentrates all request forms in a single place.
These can be broad Categories for Project Issues or forms from other modules, such as CRM Claims or HR Leave requests.

The items/categories available are defined in Project » Configuration » Issue » Categories.
Each one is representend by an icon and a description.
When clicking on a Service Desk item, the module will find what Action should be executed.
It this defition is found on it's form or on a parent, it will be used. 
If not, it an Action opening the Project Issue's default form will be used.

When opening the Action, two variables are set in the "context":
  * A default master Category (`default_master_categ_id`), the id of the selected Category.
  * A default Service Team (`default_section_id`), from the selected Category or it's parents.

For a quick start the module installs two Actions to be used here:
  * "Standard Issues": opens the form installed with the Project Issue module.
  * "New Issues": opens a showcase Project Issue form installed with this module.

The showcase form demonstrates the usage of these two default values: 
the Issue's Category selection list is limited to the Service Desk category children, 
and the Service Team is automatically selected.
""",
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': [
        'project_issue',
        'project_issue_department',
        'project_issue_sequences',
        'crm_categ_hierarchy',
    ],
    'update_xml': [
        'project_issue_view.xml',
        'crm_categ_view.xml',
    ],
    'installable': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
