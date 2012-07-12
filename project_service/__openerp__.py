# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2011
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
    'name': 'Project specific developments',
    'version': '6.1.1',
    "category": "Project Management",
    'description': """\
Service Management extension for the Project modules.
Projects: (...)
Issues: (...)
Tasks: (...)
Billing: (...)
Stock: (...)
""",
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': [
        'report_webkit',
        'hr',
        'project',              #=> "product", "analytic", "board"
        'project_functional_blocks',
        'project_issue',        #=> 'crm', 'project'
        'project_timesheet',    #=> 'project', 'hr_timesheet_sheet', 'hr_timesheet_invoice'
        'project_service_base',
    ],
    'init_xml': [
#        'reis_project_issue_data.xml',
    ],
    'update_xml': [
        'reis_project_view.xml',
        'reis_project_issue_view.xml',
        'reis_crm_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
