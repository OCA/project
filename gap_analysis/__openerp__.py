# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Xiaopeng Xie
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
    'name': 'Gap Analysis',
    'category': 'project',
    'summary': 'Gap Analysis',
    'version': '8.0.0.0.2',
    'website': 'www.elico-corp.com',
    "author": "<AUTHOR(S)>, Odoo Community Association (OCA)",
    'depends': [
        'base',
        'web_ckeditor4',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/gap_sequnece.xml',
        'views/business_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
