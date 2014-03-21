# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2010-2013 Akretion LDTA (<http://www.akretion.com>).
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


{
    'name': 'Sale Project Base',
    'version': '7.0',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """This module is a base module that give the possibility to
    create a project from a quotation""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'project',
        'sale',
    ],
    'demo': [],
    'data': [
        'sale_view.xml',
    ],
    'installable': True,
}
