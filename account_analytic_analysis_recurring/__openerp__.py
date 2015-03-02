# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Contracts Management recurring',
    'version': '0.1',
    'category': 'Other',
    'description': """
This module adds a new feature in contracts to manage recurring invoicing
=========================================================================

This is a backport of the new V8 feature available in trunk and saas. With
the V8 release this module will be deprecated.

It also adds a little feature, you can use #START# and #END# in the contract
line description to automatically insert the dates of the invoiced period.

Backport done By Yannick Buron.
""",
    'author': "OpenERP SA,Odoo Community Association (OCA)",
    'website': 'http://openerp.com',
    'depends': ['base', 'account_analytic_analysis'],
    'data': [
        'security/ir.model.access.csv',
        'account_analytic_analysis_recurring_cron.xml',
        'account_analytic_analysis_recurring_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'images': [],
}
