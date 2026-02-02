# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest import mock

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.mail.models.mail_thread import MailThread
from odoo.addons.project.models.project_project import ProjectProject


class TestProjectmarginAlert(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids += cls.env.ref("project.group_project_manager")

        cls.user_a = cls.env["res.users"].create(
            {"name": "User A", "login": "testa@test.com"}
        )
        cls.user_a.group_ids |= cls.env.ref("project.group_project_user")

        cls.partner = cls.env["res.partner"].create(
            {"name": "Georges", "email": "georges@project-margin.com"}
        )

        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Plan A",
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Project - AA",
                "code": "AA-1234",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Project",
                "partner_id": cls.partner.id,
                "account_id": cls.analytic_account.id,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Task",
                "project_id": cls.project.id,
            }
        )
        cls.project_margin_items_empty = {
            "revenues": {"data": [], "total": {"invoiced": 0.0, "to_invoice": 0.0}},
            "costs": {"data": [], "total": {"billed": 0.0, "to_bill": 0.0}},
        }
        cls.project_margin_items_90 = {
            "revenues": {"data": [], "total": {"invoiced": 90.0, "to_invoice": 0.0}},
            "costs": {"data": [], "total": {"billed": -100.0, "to_bill": 0.0}},
        }
        cls.project_margin_items_33 = {
            "revenues": {"data": [], "total": {"invoiced": 100.0, "to_invoice": 0.0}},
            "costs": {"data": [], "total": {"billed": -75.0, "to_bill": 0.0}},
        }
        cls.project_margin_items_15 = {
            "revenues": {"data": [], "total": {"invoiced": 100.0, "to_invoice": 0.0}},
            "costs": {"data": [], "total": {"billed": -90.0, "to_bill": 0.0}},
        }
        cls.project_margin_items_75 = {
            "revenues": {"data": [], "total": {"invoiced": 75.0, "to_invoice": 0.0}},
            "costs": {"data": [], "total": {"billed": -100.0, "to_bill": 0.0}},
        }
        cls.project_margin_items_100 = {
            "revenues": {"data": [], "total": {"invoiced": 75.0, "to_invoice": 0.0}},
            "costs": {"data": [], "total": {"billed": 0, "to_bill": 0.0}},
        }
        cls.foreign_currency = cls.env["res.currency"].create(
            {
                "name": "Chaos orb",
                "symbol": "☺",
                "rounding": 0.001,
                "position": "after",
                "currency_unit_label": "Chaos",
                "currency_subunit_label": "orb",
            }
        )
        cls.env["res.currency.rate"].create(
            {
                "name": "2016-01-01",
                "rate": "5.0",
                "currency_id": cls.foreign_currency.id,
            }
        )

    def _get_project_messages(self, project=None):
        if project is None:
            project = self.project
        return self.env["mail.message"].search(
            [("res_id", "=", project.id), ("model", "=", "project.project")]
        )

    def test_margin_not_exceeded_zero(self):
        # Set threshold at 80%
        # Get 0.0 values of invoiced/billed
        # Threshold is not exceeded
        with mock.patch.object(
            ProjectProject, "_get_profitability_items"
        ) as margin_mock:
            margin_mock.return_value = self.project_margin_items_empty
            self.project.margin_threshold = 0.2
            self.project._update_is_margin_threshold_exceeded()
            self.assertFalse(self.project.is_margin_threshold_exceeded)

    def test_margin_not_exceeded_33(self):
        # Set threshold at 80%
        # Get 0.0 values of invoiced/billed
        # Threshold is not exceeded
        with mock.patch.object(
            ProjectProject, "_get_profitability_items"
        ) as margin_mock:
            margin_mock.return_value = self.project_margin_items_33
            self.project.margin_threshold = 0.2
            self.project._update_is_margin_threshold_exceeded()
            self.assertFalse(self.project.is_margin_threshold_exceeded)

    def test_margin_not_exceeded_15(self):
        # Set threshold at 80%
        # Get 0.0 values of invoiced/billed
        # Threshold is not exceeded
        with mock.patch.object(
            ProjectProject, "_get_profitability_items"
        ) as margin_mock:
            margin_mock.return_value = self.project_margin_items_15
            self.project.margin_threshold = 0.2
            self.project._update_is_margin_threshold_exceeded()
            self.assertTrue(self.project.is_margin_threshold_exceeded)

    def test_margin_not_exceeded_no_costs(self):
        # Set threshold at 80%
        # Get 0.0 values of invoiced/billed
        # Threshold is not exceeded
        with mock.patch.object(
            ProjectProject, "_get_profitability_items"
        ) as margin_mock:
            margin_mock.return_value = self.project_margin_items_100
            self.project.margin_threshold = 0.2
            self.project._update_is_margin_threshold_exceeded()
            self.assertFalse(self.project.is_margin_threshold_exceeded)

    def test_margin_exceeded(self):
        # Set threshold at 80%
        # Get values of invoiced 90/billed(100)
        # Threshold is exceeded
        with mock.patch.object(
            ProjectProject, "_get_profitability_items"
        ) as margin_mock:
            margin_mock.return_value = self.project_margin_items_90
            self.project.margin_threshold = 0.2
            self.project._update_is_margin_threshold_exceeded()
            self.assertTrue(self.project.is_margin_threshold_exceeded)

    def test_margin_exceeded_notifications(self):
        # Set threshold at 80%
        # Get values of invoiced 90/billed(100)
        # Threshold is exceeded
        # User a is follower of project
        # Send notifications
        self.project.message_subscribe(self.user_a.partner_id.ids)
        messages_before = self._get_project_messages()
        with mock.patch.object(
            ProjectProject, "_get_profitability_items"
        ) as margin_mock:
            margin_mock.return_value = self.project_margin_items_90
            self.project.margin_threshold = 0.2
            self.project._update_is_margin_threshold_exceeded()
            self.assertTrue(self.project.is_margin_threshold_exceeded)
            self.project._cron_margin_threshold_exceeded()
        messages_after = self._get_project_messages()
        new_messages = messages_after - messages_before
        self.assertEqual(self.user_a.partner_id, new_messages.notified_partner_ids)
        self.assertTrue(
            any("Cost threshold exceeded" in message.body for message in new_messages)
        )

    def test_margin_exceeded_activity(self):
        # Set threshold at 80%
        # Get values of invoiced 90/billed(100)
        # Threshold is exceeded
        # User a is follower of project
        # Create activities
        self.project.create_margin_threshold_activity = True
        activities_before = self.env["mail.activity"].search(
            [("user_id", "=", self.env.user.id)]
        )
        with mock.patch.object(
            ProjectProject, "_get_profitability_items"
        ) as margin_mock:
            margin_mock.return_value = self.project_margin_items_90
            self.project.margin_threshold = 0.2
            self.project._update_is_margin_threshold_exceeded()
            self.assertTrue(self.project.is_margin_threshold_exceeded)
            self.project._cron_margin_threshold_exceeded()
        activities = (
            self.env["mail.activity"].search([("user_id", "=", self.env.user.id)])
            - activities_before
        )
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities.display_name, "Minimum Margin Exceeded")

    def test_margin_exceeded_mail(self):
        # Set threshold at 80%
        # Get values of invoiced 90/billed(100)
        # Threshold is exceeded
        # User a is follower of project
        # Send mail
        self.project.force_margin_threshold_notification = True
        with mock.patch.object(
            ProjectProject, "_get_profitability_items"
        ) as margin_mock:
            margin_mock.return_value = self.project_margin_items_90
            self.project.margin_threshold = 0.2
            self.project._update_is_margin_threshold_exceeded()
            self.assertTrue(self.project.is_margin_threshold_exceeded)
            with mock.patch.object(MailThread, "message_post_with_source") as post_mock:
                self.project._cron_margin_threshold_exceeded()
                post_mock.assert_called()
