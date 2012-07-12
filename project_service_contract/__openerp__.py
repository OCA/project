# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################


{
    'name': 'Project specific developments',
    'version': '6.1-1',
    "category": "Project Management",
    'description': """ """,
    'author': 'Julius Network Solution',
    'website': 'www.julius.fr',
    'depends': [
        'report_webkit',
		'hr',
		'project',  			#=> "product", "analytic", "board"
		'project_functional_blocks',
        'project_issue',		#=> 'crm', 'project'
        'project_timesheet',	#=> 'project', 'hr_timesheet_sheet', 'hr_timesheet_invoice'
        'base_contract',
        'project_service',
    ],
    'init_xml': [],
    'update_xml': [
        'contract_view.xml',
        'security/contract_security.xml',
#        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
