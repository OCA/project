# -*- coding: utf-8 -*-
# Author: Davide Corio
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
import odoo.tests.common as common


class TestMultiCurrencyTimesheet(common.TransactionCase):

    def setUp(self):
        super(TestMultiCurrencyTimesheet, self).setUp()
        company_model = self.env['res.company']
        rate_model = self.env['res.currency.rate']
        project_model = self.env['project.project']
        task_model = self.env['project.task']
        employee_model = self.env['hr.employee']

        # I Set up 2 new companies to test the multi-company/multi-currency
        # expected behavior
        self.company_fr = company_model.create(
            {
                'name': 'CompanyFR',
                'currency_id': self.env.ref('base.EUR').id})
        self.company_us = company_model.create(
            {
                'name': 'CompanyUS',
                'currency_id': self.env.ref('base.USD').id})
        base_company = self.env.ref('base.main_company')

        # I Create a new user, a new employee and set up the timesheet cost
        self.user_fr = self.env.ref('base.user_demo')
        self.user_fr.company_ids = [
            (6, 0, [base_company.id, self.company_fr.id, self.company_us.id])]
        self.user_fr.company_id = self.company_fr.id
        self.employee_fr = employee_model.create(
            {
                'name': 'Employee FR',
                'user_id': self.user_fr.id,
                'company_id': self.company_fr.id,
            })
        self.employee_fr.timesheet_cost = 110.0

        # I Set up 2 different rates within the same week
        self.us_rate_1 = rate_model.create(
            {
                'rate': 0.9,
                'currency_id': self.env.ref('base.USD').id,
                'name': time.strftime('%Y-05-08'),
                'company_id': self.company_fr.id,
            })
        self.us_rate_2 = rate_model.create(
            {
                'rate': 0.95,
                'currency_id': self.env.ref('base.USD').id,
                'name': time.strftime('%Y-05-10'),
                'company_id': self.company_fr.id,
            })

        # I create a new project for the US company and a new task
        self.project_USD = project_model.create(
            {
                'name': 'project_USD',
                'company_id': self.company_us.id,
            })

        self.task_USD = task_model.create(
            {
                'name': 'Task USD',
                'user_id': self.user_fr.id,
                'project_id': self.project_USD.id,
            })

    def test_account_currency(self):
        # I test that the currency for the new project is USD
        self.assertEqual(
            self.project_USD.analytic_account_id.currency_id.name, 'USD')

    def test_week_analytic_lines(self):

        # I create analytic lines for every day of the week
        # passing project and task to simulate the creation of analytic lines
        # through the task form
        al_model = self.env['account.analytic.line'].sudo(self.user_fr.id)
        date_05_08 = time.strftime('%Y-05-08')
        al_model.with_context(
            {'date': date_05_08}).create(
            {
                'name': 'Test USD',
                'project_id': self.project_USD.id,
                'task_id': self.task_USD.id,
                'account_id': self.project_USD.analytic_account_id.id,
                'unit_amount': 8,
                'date': date_05_08,
            })
        date_05_09 = time.strftime('%Y-05-09')
        al_model.with_context(
            {'date': date_05_09}).create(
            {
                'name': 'Test USD',
                'project_id': self.project_USD.id,
                'task_id': self.task_USD.id,
                'account_id': self.project_USD.analytic_account_id.id,
                'unit_amount': 8,
                'date': date_05_09,
            })
        date_05_10 = time.strftime('%Y-05-10')
        al_model.with_context(
            {'date': date_05_10}).create(
            {
                'name': 'Test USD',
                'project_id': self.project_USD.id,
                'task_id': self.task_USD.id,
                'account_id': self.project_USD.analytic_account_id.id,
                'unit_amount': 8,
                'date': date_05_10,
            })
        date_05_11 = time.strftime('%Y-05-11')
        al_model.with_context(
            {'date': date_05_11}).create(
            {
                'name': 'Test USD',
                'project_id': self.project_USD.id,
                'task_id': self.task_USD.id,
                'account_id': self.project_USD.analytic_account_id.id,
                'unit_amount': 8,
                'date': date_05_11,
            })
        date_05_12 = time.strftime('%Y-05-12')
        al_model.with_context(
            {'date': date_05_12}).create(
            {
                'name': 'Test USD',
                'project_id': self.project_USD.id,
                'task_id': self.task_USD.id,
                'account_id': self.project_USD.analytic_account_id.id,
                'unit_amount': 8,
                'date': date_05_12,
            })

        a_lines = self.project_USD.analytic_account_id.line_ids
        amounts = [l.amount for l in a_lines]
        amounts_currency = [l.amount_currency for l in a_lines]
        total_amount = sum(amounts)
        total_amount_currency = sum(amounts_currency)

        # I check that the currency conversion worked as expected and both
        # amount and amount_currency fields values are correct
        self.assertAlmostEqual(total_amount, -4734.52)
        self.assertAlmostEqual(total_amount_currency, -4400.0)
