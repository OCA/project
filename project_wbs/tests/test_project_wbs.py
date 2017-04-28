# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


class TestProjectWbs(common.TransactionCase):
    def setUp(self):
        super(TestProjectWbs, self).setUp()
        self.project = self.env['project.project'].create(
            {'name': 'Test project',
             'code': '0001'})
        self.parent_account = self.project.analytic_account_id
        self.project_son = self.env['project.project'].create(
            {'name': 'Test project son',
             'code': '01',
             'parent_id': self.parent_account.id})
        self.son_account = self.project_son.analytic_account_id
        self.project_grand_son = self.env['project.project'].create(
            {'name': 'Test project grand son',
             'code': '02',
             'parent_id': self.son_account.id})
        self.grand_son_account = self.project_grand_son.analytic_account_id

    def test_get_child_accounts(self):
        accounts = self.project._get_project_wbs()
        self.assertEqual(
            len(accounts), 3, 'wrong children number')

    def test_wbs_code(self):
        self.assertEqual(
            self.project.complete_wbs_code, '[0001]',
            'Incorrect WBS code')
        self.assertEqual(
            self.project_son.complete_wbs_code, '[0001/01]',
            'Incorrect WBS code')
        self.assertEqual(
            self.project_grand_son.complete_wbs_code, '[0001/01/02]',
            'Incorrect WBS code')
