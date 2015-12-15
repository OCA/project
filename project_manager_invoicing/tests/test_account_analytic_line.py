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
import unittest2

from openerp.tests.common import TransactionCase
from openerp import SUPERUSER_ID
from . import account_analytic_line


class test_account_analytic_line(TransactionCase):
    """ Test in progress. First time creating some
        The main goal is to ensure the calculation of hours in
        an account_analytic_line.
    """

    def setUp(self):
        import pdb
        pdb.set_trace()
        super(test_account_analytic_line, self).setUp()
        cr, uid = self.cr, self.uid
        self.ir_model_data = self.registry('ir.model.data')
        self.get_ref = partial(self.ir_model_data.get_object_reference,
                               self.cr, self.uid)

        __, self.user_demo = self.get_ref('base', 'user_demo')
        # Super user et changer groupe user
        __, self.user_admin = self.get_ref('base', 'user_admin')

        self.account_analytic_line = AccountAnalyticLine(orm.Model)
        account_analytic_line = {
            'product_id'}

        vals = {
            'invoiced_hours': 1,
            'unit_amount': 1,
            'state': 'draft',
            'user_id': self.user_demo,
        }
        self.line_id = account_analytic_line.create(self, vals)
        # Besoin de quoi pour la création d'une aal?
        #   quels sont les objets?
        #   quels sont les retours des fonctions?

    def test_write(self):
        """ The goal of this test is to check if the informations are
            correctly savec
        """
        import pdb
        pdb.set_trace()
        self.setUp

    def test_action_confirm(self):
        """ This action tests if the line doesn't change of status
            It uses the base user without the rights to make a confirmation
        """
        import pdb
        pdb.set_trace()

    def test_action_confirm_superuser(self):
        """ Same test as before but now the user has the rights to
            change the status of the line
        """
        import pdf
        pdb.set_trace()

    def test_action_reset_to_draft(self):
        """ All the user have the right to reset the aal to 'draft'
        """
        import pdb
        pdb.set_trace()

    def test_check(self):
        """ The check is rewritted in order to check the state of de linge
            instead of the sheetS
        """
        import pdb
        pdb.set_trace()

    def test_onchange_ot_invoice_set_invoiced_hours(self):
        """ The test check if invoiced_hours are changed according to 
            invoicing rate factor
        """
        import pdb
        pdb.set_trace()

        # La méthode dans aal est à retravailler. Pour le moment
        # NoTEST
    def test_invoice_cost_create(self):
        import pdb
        pdb.set_trace()
