# -*- coding: utf-8 -*-
import openerp
from openerp.tests import common

class test_something(common.TransactionCase):
    def setUp(self):
        super(test_something, self).setUp()
        self.record_partner1 = self.env['base.res.partner'].create({
        'name': 'Anders'})
        self.record_partner2 = self.env['base.res.partner'].create({
        'name': 'Bertil'})
        self.record_user1 = self.env['base.res.users'].create({
        'partner_id': partner1,
        'login': 'anders',
        #'company_id': 1})
        self.record_user1 = self.env['base.res.users'].create({
        'partner_id': partner2,
        'login': 'bertil',
        #'company_id': 1})
        self.record_project = self.env['project_scrum.project.scrum.sprint'].create(
        #'analytic_account_id': 1,
        #'alias_id': 1,
        'state': 'draft',
        })

    def test_something(self):
        model = self.registry('project.scrum.sprint')
        i = model.create(self.cr, SUPERUSER_ID, {
        'name': 'Testprojekt',
        'date_start': '2015-01-10',
        'date_stop': '2015-01-28',
        'project_id': x,
        'product_owner_id': y,
        'scrum_master_id' z,
        'review': 'foo',
        'retrospective': 'bar',
        'state': 'draft'})
