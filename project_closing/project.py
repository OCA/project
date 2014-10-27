# -*- coding: utf-8 -*-
from osv import orm


class project_project(orm.Model):
    _inherit = 'project.project'

    def set_done(self, cr, uid, ids, context=None):
        """ We will close related analytic account """
        analytic_account_obj = self.pool.get('account.analytic.account')
        if isinstance(ids, (int, long)):
            ids = [ids]
        projects = self.browse(cr, uid, ids, context=context)
        analytic_account_ids = [x.analytic_account_id.id for x in projects]
        if analytic_account_ids:
            analytic_account_obj.write(cr, uid,
                                       analytic_account_ids,
                                       {'state': 'close'}, context=context)
        return super(project_project, self).set_done(cr, uid,
                                                     ids, context=context)

    def set_open(self, cr, uid, ids, context=None):
        """ We will re-open related analytic account """
        analytic_account_obj = self.pool.get('account.analytic.account')
        if isinstance(ids, (int, long)):
            ids = [ids]
        projects = self.browse(cr, uid, ids, context=context)
        analytic_account_ids = [x.analytic_account_id.id for x in projects]
        if analytic_account_ids:
            analytic_account_obj.write(cr, uid,
                                       analytic_account_ids,
                                       {'state': 'open'}, context=context)
        return super(project_project, self).set_open(cr, uid,
                                                     ids, context=context)
