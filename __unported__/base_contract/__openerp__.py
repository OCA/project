# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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
    'name': 'Base Contract',
    'version': '1.0',
    'category': 'Generic Modules/Base',
    'description': """

Presentation:

This module allows you to manage your contracts entirely.
It allows you to define the model you want to add to a contract.
It automatically adds a link to the contracts on the model view.


Configuration:

Administration>Configuration>Contracts

* Generate Contract Types:
Inform the model which you would like to create the type of contract, name and code of the type of contract to automatically generate the type of contract.

* Contract Types:
Contract types generated are listed here.

* Contract category:
Creating the type of contract with a code and a name.


Links of the contract in the model informed:

* The link of the contract is put in the links column on the menu of the selected model when generating the model contract.

* Example: Contrat du Sales Order:
Learn the name, ref, date of start and end of the contract, the Kind of contract, the bond, the date of the first billing, the amount, the Company ...

    """,
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr',
    'depends': [
                'base',
                'analytic',
                ],
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'base_contract_view.xml',
        'wizard/generate_view.xml',
    ],
    'demo_xml': [],
    'images' : ['images/Contract category.png','images/Contract Sales Order.png','images/Contract Types.png','images/Generate Contract Types.png'],
    'test': [],
    'installable': False,
    'active': False,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
