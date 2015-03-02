# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Akretion LDTA (<http://www.akretion.com>).
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

{'name': 'Project requiring functional blocks',
 'version': '1.2',
 'author': "Akretion,Odoo Community Association (OCA)",
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'description': """
Adds functional blocks to organize the projects tasks.
 """,
 'depends': [
     'project',
 ],
 'data': [
     'security/ir.model.access.csv',
     'project_view.xml',
 ],
 'demo': [
     'project_demo.xml',
 ],
 'installable': False,
 'application': True,
}
