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

    def _get_department(self, cr, uid, ids, context=None):
        employee_obj = self.pool['hr.employee']
        department_id = False
        employee_ids = employee_obj.search(cr, uid, [('user_id','=', uid)])
        if employee_ids:
            employee = employee_obj.browse(cr, uid, 
                                                employee_ids[0], 
                                                context=context)
            if employee.department_id:
                department_id = employee.department_id.id
        return department_id

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
            readonly=True,
            help="Account's related department"),
    }

    _defaults = {
        'department_id': _get_department,
    }

       