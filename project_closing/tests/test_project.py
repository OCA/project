# -*- coding: utf-8 -*-
from odoo import tests


class TestProject(tests.TransactionCase):
    def setUp(self):
        super(TestProject, self).setUp()
        self._project1 = self.env['project.project'].create({
            'name': "Some test project"})
        self._analytic1 = self._project1.analytic_account_id
        self._project2 = self.env['project.project'].create({
            'name': "Some sibling project",
            'analytic_account_id': self._analytic1.id})

    def test_project_toggle_active(self):
        # By default, the Project and Analytic Account are active
        self.assertTrue(self._project1.active)
        self.assertTrue(self._project1.analytic_account_id.active)
        # Inactivating a Project inactivates the parent Analytic
        # and the sibling Projects
        self._project1.toggle_active()
        self.assertFalse(self._project1.active)
        self.assertFalse(self._project2.active)
        self.assertFalse(self._analytic1.active)
        # Reactivating a Project also reactivated the parent Analytic
        # and the sibling Projects
        self._project1.toggle_active()
        self.assertTrue(self._project1.active)
        self.assertTrue(self._project2.active)
        self.assertTrue(self._analytic1.active)

    def test_analytic_toggle_active(self):
        # By default, the Project and Analytic Account are active
        self.assertTrue(self._project1.active)
        self.assertTrue(self._analytic1.active)
        # Inactivating an Analytic Account inactivates child Projects
        self._analytic1.toggle_active()
        self.assertFalse(self._project1.active)
        self.assertFalse(self._project2.active)
        self.assertFalse(self._analytic1.active)
        # Reactivating an Analytic Account reactivates child Projects
        self._project1.toggle_active()
        self.assertTrue(self._project1.active)
        self.assertTrue(self._project2.active)
        self.assertTrue(self._analytic1.active)
