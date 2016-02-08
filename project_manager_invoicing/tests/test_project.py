# -*- coding: utf-8 -*-
#
#    Author: Denis Leemann
#    Copyright 2015 Camptocamp SA
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
from functools import partial

from openerp.tests.common import TransactionCase
from openerp import SUPERUSER_ID









class test_project(TransactionCase):
    """ Test the working of hours calculation with invoiced_hours    
        The purpose of the test is to check if the calculation of hours,
        formerly based on unit_amount, is done correctly.
    """

# TODO Creation des test. Lors de la création, le projet doit avoir
#    un durée initiale = 100 (au minimum plus grande que 0)

    def setUp(self):
        super(test_project, self).setUp()
        cr, uid = self.cr, self.uid
        self.ir_model_data = self.registry('ir.model.data')
        self.get_ref = partial(self.ir_model_data.get_object_reference,
                               self.cr, self.uid)

        __, self.user_demo = self.get_ref('base', 'user_demo')
        # __, self.user_admin = self.get_ref('base', 'user_admin')

        self.project_model = self.registry('project.project')
        self.aal_model = self.registry('account.analytic.line')
        self.product_model = self.registry('product.product')

        vals = {
            'alias_model': 'alias_model',  # check char varying
            'alias_id': 1,  # check
            'privacy_visibility': 'false',  # check char varying
            'analytic_account_id': 1,  # check => reprendre celui des AAL
        }


        self.vals_aal = {
            'invoiced_hours': 1,
            'unit_amount': 1,
            'state': 'draft',
            'user_id': self.user_demo,  # OK
            'product_id': 1,  # check
            'journal_id': 1,  # Check
            'account_id': 2,  # check => fonctionne avec ce compte, voir ce que c'est en particulier
            'unit_amount': 1,  # check
            'name': 'name'
        }
        self.aal_id = self.aal_model.create(cr, uid, self.vals_aal)
        # self.project_id = self.project_model.create(cr, uid, vals)


# ***** AJOUT NOTEPAD
# TASK_WATCHERS = [
#     'work_ids',
#     'remaining_hours',
#     'effective_hours',
#     'planned_hours'
# ]
# TIMESHEET_WATCHERS = [
#     'unit_amount',
#     'product_uom_id',
#     'account_id',
#     'task_id',
#     'invoiced_hours'
# ]
# ***** FIN AJOUT NOTEPAD

# # NOT NULL VALUES
# id
# alias_model
# alias_id
# privacy_visibility
# analytic_account_id
# state

# # VALUES importantes
# effective_hours
# planned_hours
# total_hours
# progress_rate

    # Un override de la fonction de base
    def test_progress_rate(self):
    	pass
        # import pdb; pdb.set_trace()
        # cr, uid = self.cr, self.uid
        # # context = self.aal_id
        # aal = self.aal_model._check(cr, uid, ids=self.aal_id)
        # roro ='roro'
        # assertEqual(aal.state,'draft')

    # Revoir code de la fonction de base
    def test_store_set_values(self):
    	cr, uid = self.cr, self.uid
        pass
    # La fonction de base semble marcher

    def test_get_hours(self):
    # Regarder quand la fonction de base est utilisée
    	cr, uid = self.cr, self.uid
        pass

    def test_get_analytic_line(self):
    	cr, uid = self.cr, self.uid
        pass
