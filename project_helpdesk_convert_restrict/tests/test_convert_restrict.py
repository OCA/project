# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestConvertRestrict(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company
        # This module is independent of project_no_portal; if that module is
        # also installed, make sure its portal-visibility block is off so the
        # fixtures below can use "portal" projects.
        if "block_project_portal_access" in cls.company._fields:
            cls.company.block_project_portal_access = False
        cls.team = cls.env["helpdesk.team"].create({"name": "Test Team"})
        cls.employees_project = cls.env["project.project"].create(
            {
                "name": "Employees Project",
                "privacy_visibility": "employees",
                "company_id": cls.company.id,
            }
        )
        cls.portal_project = cls.env["project.project"].create(
            {
                "name": "Portal Project",
                "privacy_visibility": "portal",
                "company_id": cls.company.id,
            }
        )
        cls.employees_task = cls.env["project.task"].create(
            {"name": "Employees Task", "project_id": cls.employees_project.id}
        )
        cls.portal_task = cls.env["project.task"].create(
            {"name": "Portal Task", "project_id": cls.portal_project.id}
        )

    def _set_restrict(self, enabled):
        self.company.restrict_ticket_conversion = enabled

    def test_restrict_off_allows_any_project(self):
        # Standard behaviour: conversion opens the wizard whatever the visibility.
        self._set_restrict(False)
        action = self.employees_task.action_convert_to_ticket()
        self.assertEqual(action["res_model"], "project.task.convert.wizard")

    def test_restrict_on_blocks_non_portal_project(self):
        self._set_restrict(True)
        with self.assertRaises(UserError):
            self.employees_task.action_convert_to_ticket()

    def test_restrict_on_allows_portal_project(self):
        self._set_restrict(True)
        action = self.portal_task.action_convert_to_ticket()
        self.assertEqual(action["res_model"], "project.task.convert.wizard")

    def test_restrict_on_blocks_mixed_batch(self):
        self._set_restrict(True)
        tasks = self.employees_task | self.portal_task
        with self.assertRaises(UserError):
            tasks.action_convert_to_ticket()
