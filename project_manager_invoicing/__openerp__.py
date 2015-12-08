# -*- coding: utf-8 -*-
#
#    Author: Yannick Vaucher, ported by Denis Leemann
#    Copyright 2015 Camptocamp SA
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
{'name': 'Project Manager Invoicing',
 'version': '7.0.1.0',
 'author': 'Camptocamp,Odoo Community Association (OCA)',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Project',
 'complexity': "normal",
 'depends': [
     'project',
     'hr_timesheet_invoice',
     'hr_timesheet_sheet',
     'hr_timesheet_task',
     'timesheet_task',
 ],
 'website': 'www.camptocamp.com',
 'data': [
    'views/account_analytic_line.xml',
    'views/hr_analytic_timesheet.xml',
    'views/project.xml',
    'wizard/analytic_line_validator_view.xml',
 ],
 'test': [
 	'test_account_analytic_line',

 ],
 'installable': True,
 'auto_install': False,
 }

