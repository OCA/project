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
    'name': 'Project Issue Sequences',
    'version': '0.1',
    "category": "Project Management",
    'description': """\
Reference sequences for Issues, configurable by Category.
For example: an IT Management related issue might have a "IT-xxxxx" sequence, and a Building maintenance issue an independent "B-xxxx" sequence.  
If no specific Sequence is specified, the default "Project Issue" sequence will be used.
If the crm_categ_hierarchy module is also installed, specific sequences will apply to all child categories. 
""",
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': ['project_issue'], 
    'data': [
        'crm_categ_view.xml', 
        'project_issue_view.xml', 
        'project_issue_data.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
