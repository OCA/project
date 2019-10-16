# Copyright 2017-19 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
from odoo.exceptions import ValidationError


class TestProjectWbs(common.TransactionCase):

    def setUp(self):
        super(TestProjectWbs, self).setUp()

        self.project_project = self.env['project.project']

        self.project = self.project_project.create(
            {'name': 'Test project',
             'code': '0001'})
        self.parent_account = self.project.analytic_account_id
        self.project_son = self.project_project.create(
            {'name': 'Test project son',
             'code': '01',
             'parent_id': self.parent_account.id})
        self.son_account = self.project_son.analytic_account_id
        self.project_grand_son = self.project_project.create(
            {'name': 'Test project grand son',
             'code': '02',
             'parent_id': self.son_account.id})
        self.grand_son_account = self.project_grand_son.analytic_account_id
        self.project2 = self.project_project.create(
            {'name': 'Test project 2',
             'code': '03'})
        self.account2 = self.project2.analytic_account_id

        self.analytic_account = self.env['account.analytic.account'].create({
            'name': 'Test analytic account',
        })

    def test_get_name_and_code(self):
        project = self.project_project.create(
            {'name': 'Project',
             'code': '1001'})
        project.name_get()
        project_account = self.project.analytic_account_id
        project_account.name_get()

    def test_get_project_wbs(self):
        accounts = self.project._get_project_wbs()
        self.assertEqual(len(accounts), 3, 'wrong children number')

    def test_wbs_code(self):
        self.assertEqual(
            self.project.complete_wbs_code, '[0001]',
            'Incorrect WBS code')
        self.assertEqual(
            self.project_son.complete_wbs_code, '[0001 / 01]',
            'Incorrect WBS code')
        self.assertEqual(
            self.project_grand_son.complete_wbs_code, '[0001 / 01 / 02]',
            'Incorrect WBS code')

    def test_get_child_accounts(self):
        res = self.env['account.analytic.account'].get_child_accounts()
        self.assertEqual(res, {}, 'Should get nothing')
        res = self.parent_account.get_child_accounts()
        for has_parent in res.keys():
            self.assertEqual(res[has_parent], True, 'Wrong child accounts')

    def test_view_context(self):
        res = self.project_project.with_context(
            default_parent_id=self.project.id).\
            _resolve_analytic_account_id_from_context()
        self.assertEqual(
            res, self.project.id, 'Wrong Parent Project from context')
        res = self.project_project.\
            _resolve_analytic_account_id_from_context()
        self.assertEqual(
            res, None, 'Should not be anything in context')

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

    def test_onchange_parent(self):
        self.project2.write({'parent_id': self.parent_account.id})
        self.project2.on_change_parent()
        child_in = self.project2 in self.project.project_child_complete_ids
        self.assertTrue(child_in, 'Child not added')

    def test_duplicate(self):
        seq_id = self.env['ir.sequence'].search(
            [('code', '=', 'account.analytic.account.code')])
        next_val = seq_id.number_next_actual
        copy_project = self.project.copy()
        self.assertTrue(str(next_val) in copy_project.analytic_account_id.code)
        next_val = seq_id.number_next_actual
        with self.assertRaises(ValidationError):
            copy_analytic = self.parent_account.copy()
            self.assertTrue(
                str(next_val) in copy_analytic.analytic_account_id.code)
        self.analytic_account.copy()

    def test_project_analytic_id(self):
        self.grand_son_account.account_class = 'deliverable'
        self.grand_son_account._compute_project_analytic_id()
        self.assertEqual(
            self.grand_son_account.project_analytic_id.id,
            self.son_account.id)
