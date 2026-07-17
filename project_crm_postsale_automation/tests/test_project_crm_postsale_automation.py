# Copyright 2026 Patryk Pyczko (Nagarro)<patryk.pyczko@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProjectCrmPostsaleAutomation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sales_team = cls.env["crm.team"].create({"name": "Post-sale Test Team"})
        cls.sales_user = cls.env["res.users"].create(
            {
                "name": "Post-sale Responsible User",
                "login": "postsale_user",
                "email": "postsale@example.com",
                "groups_id": [(4, cls.env.ref("sales_team.group_sale_salesman").id)],
            }
        )
        cls.sales_user.write({"sale_team_id": cls.sales_team.id})
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Customer", "email": "customer@example.com"}
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Post-sale Project",
                "partner_id": cls.partner.id,
                "postsale_active": True,
                "postsale_user_id": cls.sales_user.id,
                "postsale_interval": 1,
                "postsale_rule": "months",
                "postsale_day_of_month": 15,
                "postsale_next_date": date(2026, 7, 15),
                "postsale_notes": "<h1>SLA Target</h1><p>Follow up within 48 hours</p>",
            }
        )

    def test_01_postsale_configuration_constraints(self):
        """Test that invalid configurations trigger
        configuration errors."""
        with self.assertRaises(UserError):
            self.project.write({"postsale_user_id": False})

        with self.assertRaises(UserError):
            self.project.write({"postsale_interval": 0})

        with self.assertRaises(UserError):
            self.project.write({"postsale_interval": -5})

        with self.assertRaises(UserError):
            self.project.write({"postsale_day_of_month": 0})

        with self.assertRaises(UserError):
            self.project.write({"postsale_day_of_month": 32})

        with self.assertRaises(UserError):
            self.project.write({"postsale_name_template": "{invalid_variable}"})

    def test_02_onchange_postsale_active(self):
        """Test that postsale_partner_id is pre-filled from project partner."""
        new_project = self.env["project.project"].new(
            {"partner_id": self.partner.id, "postsale_active": True}
        )
        new_project._onchange_postsale_active()
        self.assertEqual(new_project.postsale_partner_id, self.partner)

    def test_03_calculate_next_date_handling(self):
        """Test calculation parameters across day, week, month and
        safe end of month transitions."""
        self.project.write(
            {
                "postsale_interval": 12,
                "postsale_rule": "days",
                "postsale_day_of_month": 1,
            }
        )
        next_date = self.project._calculate_next_date(date(2026, 7, 1))
        self.assertEqual(next_date, date(2026, 7, 13))

        self.project.write({"postsale_interval": 2, "postsale_rule": "weeks"})
        next_date = self.project._calculate_next_date(date(2026, 7, 1))
        self.assertEqual(next_date, date(2026, 7, 15))

        self.project.write(
            {
                "postsale_interval": 1,
                "postsale_rule": "months",
                "postsale_day_of_month": 31,
            }
        )
        next_date = self.project._calculate_next_date(date(2026, 8, 31))
        self.assertEqual(next_date, date(2026, 9, 30))

        self.project.write({"postsale_interval": 1, "postsale_rule": "quarters"})
        next_date = self.project._calculate_next_date(date(2026, 1, 31))
        self.assertEqual(next_date, date(2026, 4, 30))

        self.project.write({"postsale_interval": 1, "postsale_rule": "semesters"})
        next_date = self.project._calculate_next_date(date(2026, 1, 15))
        self.assertEqual(next_date, date(2026, 7, 31))

        self.project.write({"postsale_interval": 1, "postsale_rule": "years"})
        next_date = self.project._calculate_next_date(date(2024, 2, 29))
        self.assertEqual(next_date, date(2025, 2, 28))

    def test_04_period_labels(self):
        """Test period formatting labels mapping code variables."""
        self.project.write({"postsale_rule": "days"})
        label = self.project._get_period_label(date(2026, 1, 1))
        self.assertEqual(label, "Day 01")

        self.project.write({"postsale_rule": "weeks"})
        label = self.project._get_period_label(date(2026, 1, 5))
        self.assertEqual(label, "W2")

        self.project.write({"postsale_rule": "months"})
        label = self.project._get_period_label(date(2026, 7, 20))
        self.assertEqual(label, "July")

        self.project.write({"postsale_rule": "quarters"})
        label = self.project._get_period_label(date(2026, 5, 20))
        self.assertEqual(label, "Q2")

        self.project.write({"postsale_rule": "semesters"})
        label = self.project._get_period_label(date(2026, 8, 10))
        self.assertEqual(label, "S2")

        self.project.write({"postsale_rule": "years"})
        label = self.project._get_period_label(date(2026, 7, 20))
        self.assertEqual(label, "Annual")

    def test_05_manual_and_cron_lead_generation(self):
        """Test opportunity execution engine pipelines, preventing
        duplicates and tracking metrics."""
        initial_count = self.project.postsale_lead_count
        self.assertEqual(initial_count, 0)

        target_generation_date = self.project.postsale_next_date
        self.project.action_generate_postsale_opportunity()

        self.project._compute_postsale_lead_count()
        self.assertEqual(self.project.postsale_lead_count, 1)

        lead = self.env["crm.lead"].search(
            [("project_id", "=", self.project.id), ("is_postsale", "=", True)],
            limit=1,
        )
        self.assertTrue(lead.exists())
        self.assertEqual(lead.postsale_cycle_date, target_generation_date)
        self.assertEqual(lead.user_id, self.sales_user)
        self.assertEqual(lead.team_id, self.sales_team)
        self.assertEqual(lead.partner_id, self.partner)
        self.assertEqual(lead.description, self.project.postsale_notes)

        expected_next_date = self.project._calculate_next_date(target_generation_date)
        self.assertEqual(self.project.postsale_last_date, target_generation_date)
        self.assertEqual(self.project.postsale_next_date, expected_next_date)

        # Call again on the same target date to verify duplicate
        # prevention logic handles timeline healing
        self.project.write({"postsale_next_date": target_generation_date})
        self.project.action_generate_postsale_opportunity()
        self.project._compute_postsale_lead_count()
        self.assertEqual(self.project.postsale_lead_count, 1)

    def test_06_cron_execution_target_filtering(self):
        """Test automated scheduler scope validations
        against current date constraints."""
        self.project.write({"postsale_next_date": date(2026, 12, 31)})
        self.env["project.project"]._cron_generate_postsale_opportunities()
        self.assertEqual(self.project.postsale_lead_count, 0)

        self.project.write({"postsale_next_date": date(2026, 6, 1)})
        self.env["project.project"]._cron_generate_postsale_opportunities()
        self.project._compute_postsale_lead_count()
        self.assertEqual(self.project.postsale_lead_count, 1)

    def test_07_chatter_logging_on_write(self):
        """Test framework chatter tracking outputs values correctly on
        status change operations."""
        self.project.write({"postsale_active": False})
        messages = self.project.message_ids.mapped("body")
        self.assertTrue(
            any("Post-sale tracking DEACTIVATED." in msg for msg in messages)
        )

        self.project.write({"postsale_active": True})
        messages = self.project.message_ids.mapped("body")
        self.assertTrue(any("Post-sale tracking ACTIVATED." in msg for msg in messages))

    def test_08_html_next_executions_preview_localization(self):
        """Test compute field renders html layout strings and supports
        lang format parameters."""
        self.project.write({"postsale_next_date": date(2026, 7, 15)})
        self.project._compute_postsale_next_executions()
        self.assertIn("<ul>", self.project.postsale_next_executions)

        # Force a localized user format to make sure format_date
        # logic executes correctly. Use with_context (non-mutating) so the
        # lang override doesn't leak into the shared env of other tests.
        self.env["res.lang"]._activate_lang("es_ES")
        project_es = self.project.with_context(lang="es_ES")
        project_es._compute_postsale_next_executions()
        self.assertTrue(bool(project_es.postsale_next_executions))

        self.project.write({"postsale_active": False})
        self.project._compute_postsale_next_executions()
        self.assertIn("Not active", self.project.postsale_next_executions)

    def test_09_inactive_and_tag_disabled_handling(self):
        """Verify early returns exit cleanly without state modification when
        features are deactivated."""
        # 1. Test early exit when postsale_active is False
        self.project.write({"postsale_active": False})
        baseline_date = self.project.postsale_next_date

        self.project.action_generate_postsale_opportunity()
        self.assertEqual(self.project.postsale_next_date, baseline_date)

        # 2. Test early exit when tags generation is disabled
        self.project.write({"postsale_active": True, "postsale_generate_tags": False})
        tags = self.project._get_postsale_tags(date(2026, 7, 15), "Q2")
        self.assertEqual(tags, [])

    def test_10_action_view_postsale_leads(self):
        """Verify the window action returns the correct model target,
        domain filters, and default context payload."""
        action = self.project.action_view_postsale_leads()

        self.assertEqual(action["res_model"], "crm.lead")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["view_mode"], "list,form")

        expected_domain = [
            ("project_id", "=", self.project.id),
            ("is_postsale", "=", True),
        ]
        self.assertEqual(action["domain"], expected_domain)
        self.assertEqual(action["context"], {"default_project_id": self.project.id})

    def test_11_next_executions_configuration_error(self):
        """Test that the preview shows the configuration error message
        for records that carry an invalid configuration (e.g. virtual
        records not yet gone through the write constraints)."""
        new_project = self.env["project.project"].new(
            {
                "name": "Invalid Config Project",
                "postsale_active": True,
                "postsale_next_date": date(2026, 7, 15),
                "postsale_rule": "months",
                "postsale_day_of_month": 32,
            }
        )
        new_project._compute_postsale_next_executions()
        self.assertIn("Configuration Error", new_project.postsale_next_executions)

    def test_12_format_postsale_name_exception_fallback(self):
        """Test the fallback naming when the template fails to render,
        bypassing ORM constraints with a direct SQL update to simulate
        a template that turned invalid after being saved."""
        self.env.cr.execute(
            "UPDATE project_project SET postsale_name_template = %s WHERE id = %s",
            ("{invalid", self.project.id),
        )
        self.project.invalidate_recordset(["postsale_name_template"])
        name = self.project._format_postsale_name(date(2026, 7, 15), "Q1")
        self.assertEqual(name, f"Q1 2026 - {self.project.name}")

    def test_13_cron_exception_handling_logs_error(self):
        """Test that an unexpected error during generation is caught
        and logged instead of interrupting the whole cron batch."""
        self.project.write({"postsale_next_date": date(2026, 6, 1)})
        with patch.object(
            type(self.project),
            "action_generate_postsale_opportunity",
            side_effect=Exception("boom"),
        ):
            self.env["project.project"]._cron_generate_postsale_opportunities()

        log_entry = (
            self.env["ir.logging"]
            .sudo()
            .search([("func", "=", "_cron_generate_postsale_opportunities")], limit=1)
        )
        self.assertTrue(log_entry)
        self.assertIn("boom", log_entry.message)
