# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class AnalyticAccount(orm.Model):
    _inherit = "account.analytic.account"
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
    }


class AnalyticLine(orm.Model):
    _inherit = "account.analytic.line"
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
    }
