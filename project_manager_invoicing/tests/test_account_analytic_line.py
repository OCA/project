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


class test_account_analytic_line(TransactionCase):
    """ Test in progress. First time creating some
        The main goal is to ensure the calculation of hours in
        an account_analytic_line.
    """

    def hrTester(self):
        vals_hr= {
            'company_id': 'base.main_company',
            'name': 'HR Tester',
            'login': 'hr',
            'password': 'hr',
            'group_id': 'base.group_hr_manager'
        }

        return vals_hr

    def createEmployee(self):
        return False
#creation of test helpers.

    def setUp(self):
        super(test_account_analytic_line, self).setUp()
        cr, uid = self.cr, self.uid      

# Create a user 'HR Tester'
# Create a product with type service used to specify employees designation
# Create an analytic journal form employees timesheet
# Create an employee 'HR Tester' for user 'HR Tester'
# Create a timesheet invoice factor of 100%
# Create a project 'Timesheet task and indicator tests'
# Create a task 'Test timesheet records'

        # Création des modèles
        self.user_model = self.registry('res.users')
        self.aal_model = self.registry('account.analytic.line')
        self.product_model = self.registry('product.product')
        self.aaj_model = self.registry('account.analytic.journal')
        self.project_model = self.registry('project.project')  # to check => normalement pas utilisé dans cette classe
        # self.task_model = self.registry('task.task')  #to check

        # présent de base
        self.ir_model_data = self.registry('ir.model.data')
        self.get_ref = partial(self.ir_model_data.get_object_reference,
                               self.cr, self.uid)

        __, self.user_demo = self.get_ref('base', 'user_demo')
        # Super user et changer groupe user
        # __, self.user_admin = self.get_ref('base', 'user_admin')

        vals_user = {  # valeurs reprises de l'exemple yaml
            'name' : 'HR Tester',
            'login' : 'hr',
            'password' : 'hr',
            'groups_id' : 'base.group_hr_manager'
        }
        self.user_hr = self.user_model.create(cr, uid, vals_user)

        # create an anylytic journal for employeesTS
        



        aal_vals = {
            'invoiced_hours': 1,
            'unit_amount': 1,
            'state': 'draft',
            'user_id': self.user_demo,  # OK
            'product_id': 1,  # check
            'journal_id': 1,  # Check
            'account_id': self.user_demo.account_id,  # check => fonctionne avec ce compte, voir ce que c'est en particulier
            'unit_amount': 1,  # check
            'name': 'name'
        }
        self.line_id = self.aal_model.create(cr, uid, aal_vals)

        #aal = self.aal_model.create(cr, uid, aal_vals)
        # Besoin de quoi pour la création d'une aal?
        #   quels sont les objets?
        #   quels sont les retours des fonctions?

    def test_write(self):
        """ The goal of this test is to check if the informations are
            correctly saved
        """
        cr, uid = self.cr, self.uid
        pass
        # self.aal_model.action_confirm
        # self.assertEqual(self.aal_model.state, 'confirm')

        # self.aal_model.action_reset_to_draft
        # self.assertEqual(self.aal_model.state, 'draft')

        # aal = self.aal_model.create(self.cr, self.uid, vals)

        # self.assertEqual(self.line_id, 61)
        # self.assertEqual(aal.state, 'draft')

    # def test_action_confirm(self):
    #     """ This action tests if the line doesn't change of status
    #         It uses the base user without the rights to make a confirmation
    #     """
    #     pass

    # def test_action_confirm_superuser(self):
    #     """ Same test as before but now the user has the rights to
    #         change the status of the line
    #     """
    #     pass

    # def test_action_reset_to_draft(self):
    #     """ All the user have the right to reset the aal to 'draft'
    #     """
    #     pass

    def test_check(self):
        """ The check is rewritted in order to check the state of the line
            instead of the sheets
        """
        import pdb; pdb.set_trace()
        cr, uid = self.cr, self.uid

        aal_one = self.aal_model.browse(cr, uid, self.line_id, context=None)
        print('after')
        self.assertEqual(aal_one.state, 'draft')
        # aal_one._check(context=None)
        # product = self.aal_model.action_confirm(cr, self.uid, ids={aal_one.id})
        # print(product)
        print('print')
        # self.assertEqual(aal_one.state, 'confirm')

    # def test_onchange_ot_invoice_set_invoiced_hours(self):
    #     cr, uid = self.cr, self.uid
    #     """ The test check if invoiced_hours are changed according to 
    #         invoicing rate factor
    #     """
    #     pass

    #     # La méthode dans aal est à retravailler. Pour le moment
    #     # NoTEST
    # def test_invoice_cost_create(self):
    #     cr, uid = self.cr, self.uid    
    #     pass
