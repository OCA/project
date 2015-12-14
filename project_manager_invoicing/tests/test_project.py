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

class test_project(TransactionCase):
""" Test the working of hours calculation with invoiced_hours
	
	The purpose of the test is to ckeck if the calculation of hours,
	ormerly based on unit_amount, is done correctly.
"""
	def setUp(self):
		super(test_project), self.setUp()
		cr, uid = self.cr, self.uid

		__, self.user_demo =self.get_ref('base', 'user_demo')


	# Un override de la fonction de base
	def test_progress_rate(self):

	# Revoir code de la fonction de base
	def test_store_set_values(self):

	# La fonction de base semble marcher
	def test_get_hours(self):

	# Regarder quand la fonction de base est utilisée
	def test_get_analytic_line(self):