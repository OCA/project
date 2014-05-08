# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class AnalyticAccount(orm.Model):
    _inherit = "account.analytic.account"
    _columns = {
        'department_id': fields.many2one(
            'hr.department', 
            'Department'),
    }


class AnalyticLine(orm.Model):
    _inherit = "account.analytic.line"
    _columns = {
        'department_id': fields.many2one(
            'hr.department', 
            'Department',
            help="User's related department"),
        'account_department_id': fields.related(
            'account_id',
            'department_id',
            type='many2one',
            relation='hr.department',
            string='Account Department',
            store=True,
            readonly=True
            help="Account's related department"),
    }
