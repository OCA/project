# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


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
        self.project2 = self.env['project.project'].create(
            {'name': 'Test project 2',
             'code': '03'})
        self.account2 = self.project2.analytic_account_id

    def test_get_project_wbs(self):
        accounts = self.project._get_project_wbs()
        self.assertEqual(len(accounts), 3, 'wrong children number')

    def test_wbs_code(self):
        self.assertEqual(
            self.project.complete_wbs_code, '0001',
            'Incorrect WBS code')
        self.assertEqual(
            self.project_son.complete_wbs_code, '0001/01',
            'Incorrect WBS code')
        self.assertEqual(
            self.project_grand_son.complete_wbs_code, '0001/01/02',
            'Incorrect WBS code')

    def test_get_child_accounts(self):
        res = self.parent_account.get_child_accounts()
        for has_parent in res.keys():
            self.assertEqual(res[has_parent], True, 'Wrong child accounts')

    def test_view_context(self):
        res = self.env['project.project'].with_context(
            default_parent_id=self.project.id).\
            _resolve_analytic_account_id_from_context()
        self.assertEqual(
            res, self.project.id, 'Wrong Parent Project from context')

    def test_indent_calc(self):
        self.son_account._wbs_indent_calc()
        self.assertEqual(self.son_account.wbs_indent, '>', 'Wrong Indent')

    def test_open_window(self):
        res = self.project_son.action_open_parent_tree_view()
        self.assertEqual(
            res['domain'][0][2][0], self.project.id,
            'Parent not showing in view')
        res = self.project_grand_son.action_open_child_tree_view()
        self.assertEqual(
            res['domain'][0][2], [], 'Lowest element have no child')
        res = self.project.action_open_child_kanban_view()
        self.assertEqual(
            res['domain'][0][2][0], self.project_son.id,
            'Son not showing in view')
        res = self.project_son.action_open_child_kanban_view()
        self.assertEqual(
            res['domain'][0][2][0], self.project_grand_son.id,
            'Grand son not showing in kanban view')
        res = self.project_son.action_open_parent_kanban_view()
        self.assertEqual(
            res['domain'][0][2][0], self.project.id,
            'Parent not showing in kanban view')
        res = self.project.action_open_view_project_form()
        self.assertEqual(
            res['res_id'], self.project.id,
            'Wrong project form view')

    def test_onchange(self):
        self.project2.write({'parent_id': self.parent_account.id})
        child_in = self.project2 in self.project.project_child_complete_ids
        self.assertTrue(child_in, 'Child not added')
