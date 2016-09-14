# -*- coding: utf-8 -*-
# © 2004-2010 Tiny SPRL <http://tiny.be>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Contracts Management recurring',
    'version': '7.0.0.1.1',
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
    "license": 'AGPL-3',
    'author': "OpenERP SA,Odoo Community Association (OCA)",
    'website': 'http://openerp.com',
    'depends': ['base', 'account_analytic_analysis'],
    'data': [
        'security/ir.model.access.csv',
        'account_analytic_analysis_recurring_cron.xml',
        'account_analytic_analysis_recurring_view.xml',
    ],
    'installable': True,
}
