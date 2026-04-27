# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProjectTaskCrmLead(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task = cls.env["project.task"].create({"name": "Test Task"})
        cls.lead = cls.env["crm.lead"].create(
            {"name": "Test Lead", "task_id": cls.task.id}
        )

    def test_lead_task_link(self):
        self.assertIn(self.lead, self.task.lead_ids)
        self.assertEqual(self.task.lead_count, 1)

    def test_lead_count_multi(self):
        self.env["crm.lead"].create({"name": "Test Lead 2", "task_id": self.task.id})
        self.assertEqual(self.task.lead_count, 2)

    def test_action_view_task(self):
        action = self.lead.action_view_task()
        self.assertEqual(action["res_model"], "project.task")
        self.assertEqual(action["res_id"], self.task.id)

    def test_action_view_task_no_task(self):
        lead = self.env["crm.lead"].create({"name": "Lead Without Task"})
        action = lead.action_view_task()
        self.assertFalse(action["res_id"])

    def test_action_view_leads(self):
        action = self.task.action_view_leads()
        self.assertEqual(action["res_model"], "crm.lead")
        self.assertIn(("task_id", "=", self.task.id), action["domain"])
