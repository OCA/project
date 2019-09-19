# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.account_budget_ocs.tests.common import TestAccountBudgetCommon

import time


class TestProjectChangeOrder(TestAccountBudgetCommon):

    def setup(self):
        super(TestProjectChangeOrderCommon, self).setUp()

        # Creating a project
        test_project = self.env['project.project'].create({
            'name': 'TestProject'})

        # Creating a budget
        test_budget = self.env['crossovered.budget'].create({
            'date_from': Date.from_string('%s-01-01' %
                                          (datetime.datetime.now().year + 1)),
            'date_to': Date.from_string('%s-12-31' %
                                        (datetime.datetime.now().year + 1)),
            'name': 'Budget %s' % (datetime.datetime.now().year + 1),
            'state': 'draft',
            'project_id': test_project.id
        })

        # Creating two budget lines on the budget
        test_budget_line_1 = self.env['crossovered.budget.lines'].create({
            'crossovered_budget_id': test_budget.id,
            'analytic_account_id': (
                self.ref('analytic.analytic_partners_camp_to_camp')),
            'date_from': Date.from_string('%s-01-01' %
                                          (datetime.datetime.now().year + 1)),
            'date_to': Date.from_string('%s-12-31' %
                                        (datetime.datetime.now().year + 1)),
            'general_budget_id': self.account_budget_post_purchase0.id,
            'planned_amount': 10000.0,
        })
        test_budget_line_2 = self.env['crossovered.budget.lines'].create({
            'crossovered_budget_id': test_budget.id,
            'analytic_account_id': (
                self.ref('analytic.analytic_our_super_product')),
            'date_from': Date.from_string('%s-09-01' %
                                          (datetime.datetime.now().year + 1)),
            'date_to': Date.from_string('%s-09-30' %
                                        (datetime.datetime.now().year + 1)),
            'general_budget_id': self.account_budget_post_sales0.id,
            'planned_amount': 400000.0,
        })
        # Check budget in "draft" state
        self.assertEqual(test_budget.state, 'draft')

        # Simulate pressing the "Confirm" button
        budget.action_budget_confirm()

        # Check budget in "Confirmed" state
        self.assertEqual(test_budget.state, 'confirm')

        # Simulate pressing the "Validate" button
        budget.action_budget_validate()

        # Check budget in "Validated" state
        self.assertEqual(test_budget.state, 'validate')

        # Creating a change order
        test_change_order = self.env['project.change_order'].create({
                    'name': 'TestChangeOrder',
                    'project_id': test_project.id,
                    'budget_id': test_budget.id,
                    'description': "This is a test change order."})
        # Creating a change order budget adjustment lines
        test_change_order_line_1 = self.env['project.change_order'].create({
                    'change_order_id': test_change_order.id,
                    'budget_line_id': test_budget_line_1.id,
                    'note': "Line 1 Test",
                    'value': -1000})
        test_change_order_line_2 = self.env['project.change_order'].create({
                    'change_order_id': test_change_order.id,
                    'budget_line_id': test_budget_line_2.id,
                    'note': "Line 2 Test",
                    'value': +1000})

        # Check change order in default "Draft" state
        self.assertEqual(test_change_order.stage_id.name, 'Draft')

        # Simulate pressing the "In Review" button
        test_change_order.action_review()

        # Check change order in "In Review" state
        self.assertEqual(test_change_order.stage_id.name, 'In Review')

        # Simulate pressing the "Approve" button
        test_change_order.action_approve()

        # Check change order in "Approved" state
        self.assertEqual(test_change_order.stage_id.name, 'Approved')

        # Check that values on the bugdet lines were adjusted correctly
        self.assertEqual(test_budget_line_1.planned_amount, 9000.0)
        self.assertEqual(test_budget_line_2.planned_amount, 401000.0)

        # Simulate pressing the "Cancel" button
        test_change_order.action_cancel()

        # Check change order in "Canceled" state
        self.assertEqual(test_change_order.stage_id.name, 'Canceled')

        # Check that values on the bugdet lines were adjusted correctly
        self.assertEqual(test_budget_line_1.planned_amount, 10000.0)
        self.assertEqual(test_budget_line_2.planned_amount, 400000.0)

        # Simulate pressing the "Move to Draft" button
        test_change_order.action_draft()

        # Check change order in "draft" state
        self.assertEqual(test_change_order.stage_id.name, 'Draft')
