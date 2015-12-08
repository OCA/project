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
from openerp.tests.common import TransactionCase
from openerp import SUPERUSER_ID
from . import account_analytic_line


class test_account_analytic_line(TransactionCase):

    def setUp(self):
        super(test_account_analytic_line, self).setUp()
        cr, uid = self.cr, self.uid
        self.ir_model_data = self.registry('ir.model.data')
        self.get_ref = partial(self.ir_model_data.get_object_reference,
                               self.cr, self.uid)

        __, self.user_demo = self.get_ref('base', 'user_demo')
        __, self.user_admin = self.get_ref('base', 'user_demo') ### Super user et changer groupe user

        self.account_analytic_line = AccountAnalyticLine(orm.Model)
        self.user_admin.set
        account_analytic_line = {
            'product_id':}

        vals = {
            'invoiced_hours': 1,
            'unit_amount': 1,
            'state': 'draft',
        }

    def test_write(self):
        import pdb
        pdb.set_trace()
