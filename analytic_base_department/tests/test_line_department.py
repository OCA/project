# -*- coding: utf-8 -*-
# © 2016 Yannick Vaucher (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import TransactionCase


class LineDepartmentCase(TransactionCase):

    def test_default_department(self):
        """In a new users form, a user set only the firstname."""
        aal = self.env['account.analytic.line'].sudo(self.user).new()
        department_id = aal.default_get(['department_id']).get('department_id')
        self.assertEqual(department_id, self.dep.id)

    def setUp(self):
        super(LineDepartmentCase, self).setUp()
        # base.user_demo --> hr.employee_qdp --> hr.dep_rd
        self.user = self.env.ref('base.user_demo')
        self.dep = self.env.ref('hr.dep_rd')
