# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################

{
    "name": "Partner Contract module",
    "version": "0.1",
    "author": "Julius Network Solutions",
    "website": "http://www.julius.fr/",
    "category": "Generic Modules",
    "depends": [
        "base_contract",
    ],
    "description": """ Adds automatically a contract type for partners """,
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
           "data/category_data.xml",
           "data/fields_data.xml",
           "data/type_data.xml",
           "data/actions_data.xml",
           "partner_view.xml",
    ],
    'installable': False,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
