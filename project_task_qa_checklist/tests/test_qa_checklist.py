# Copyright 2026 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests.common import TransactionCase


class TestQaChecklist(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Archive any pre-existing (e.g. demo) templates so generation is
        # deterministic against only the ones created here.
        cls.env["project.task.qa.checklist.template"].search([]).write(
            {"active": False}
        )
        cls.tag = cls.env["project.tags"].create({"name": "QA Test Tag"})
        cls.pm = cls.env["res.users"].create({"name": "QA PM", "login": "qa_pm"})
        cls.project = cls.env["project.project"].create(
            {"name": "QA Test Project", "user_id": cls.pm.id}
        )
        cls.qa_stage = cls.env["project.task.type"].create(
            {"name": "Internal Testing", "is_qa_stage": True}
        )
        cls.done_stage = cls.env["project.task.type"].create(
            {"name": "Done", "is_qa_stage": False}
        )
        cls.tmpl_general = cls.env["project.task.qa.checklist.template"].create(
            {"name": "General criterion", "always_applicable": True}
        )
        cls.tmpl_tagged = cls.env["project.task.qa.checklist.template"].create(
            {"name": "Tagged criterion", "tag_ids": [(6, 0, cls.tag.ids)]}
        )

    def _new_task(self, tags=None):
        return self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": self.project.id,
                "tag_ids": [(6, 0, tags.ids)] if tags else False,
            }
        )

    def test_checklist_generation_general_criteria(self):
        task = self._new_task()
        task.write({"stage_id": self.qa_stage.id})
        self.assertEqual(task.qa_checklist_line_ids.template_id, self.tmpl_general)

    def test_checklist_generation_with_tags(self):
        task = self._new_task(tags=self.tag)
        task.write({"stage_id": self.qa_stage.id})
        self.assertEqual(
            task.qa_checklist_line_ids.template_id,
            self.tmpl_general | self.tmpl_tagged,
        )

    def test_checklist_generation_idempotent(self):
        task = self._new_task(tags=self.tag)
        task.write({"stage_id": self.qa_stage.id})
        count = len(task.qa_checklist_line_ids)
        task.write({"stage_id": self.done_stage.id})
        task.write({"stage_id": self.qa_stage.id})
        self.assertEqual(len(task.qa_checklist_line_ids), count)

    def test_checklist_progress_compute(self):
        task = self._new_task(tags=self.tag)
        task.write({"stage_id": self.qa_stage.id})
        self.assertEqual(task.qa_checklist_state, "not_started")
        lines = task.qa_checklist_line_ids
        lines[0].state = "passed"
        self.assertEqual(task.qa_checklist_state, "in_progress")
        self.assertTrue(task.qa_checklist_progress.startswith("1/2"))
        lines[1].state = "passed"
        self.assertEqual(task.qa_checklist_state, "complete")
        lines[1].state = "failed"
        self.assertEqual(task.qa_checklist_state, "complete_with_failures")

    def test_reviewer_autofill(self):
        task = self._new_task()
        task.write({"stage_id": self.qa_stage.id})
        line = task.qa_checklist_line_ids[0]
        self.assertFalse(line.reviewed_by)
        line.state = "passed"
        self.assertEqual(line.reviewed_by, self.env.user)
        self.assertTrue(line.reviewed_date)

    def test_stage_change_warning_not_blocking(self):
        task = self._new_task(tags=self.tag)
        task.write({"stage_id": self.qa_stage.id})
        activity_before = len(task.activity_ids)
        # Leaving with pending lines must not raise.
        task.write({"stage_id": self.done_stage.id})
        self.assertEqual(task.stage_id, self.done_stage)
        self.assertEqual(len(task.activity_ids), activity_before + 1)
        self.assertTrue(
            task.message_ids.filtered(lambda m: "left a QA stage" in (m.body or ""))
        )

    def test_no_warning_when_complete(self):
        task = self._new_task()
        task.write({"stage_id": self.qa_stage.id})
        task.qa_checklist_line_ids.state = "passed"
        task.qa_evidence_url = "https://example.com/evidence"
        activity_before = len(task.activity_ids)
        task.write({"stage_id": self.done_stage.id})
        self.assertEqual(len(task.activity_ids), activity_before)

    def test_missing_evidence_warns(self):
        task = self._new_task()
        task.write({"stage_id": self.qa_stage.id})
        task.qa_checklist_line_ids.state = "passed"
        activity_before = len(task.activity_ids)
        # Checklist complete but no evidence loaded must still warn.
        task.write({"stage_id": self.done_stage.id})
        self.assertEqual(len(task.activity_ids), activity_before + 1)
        self.assertTrue(
            task.message_ids.filtered(
                lambda m: "No QA evidence loaded" in (m.body or "")
            )
        )

    def test_manual_button_regenerate(self):
        task = self._new_task()
        task.write({"stage_id": self.qa_stage.id})
        self.assertEqual(len(task.qa_checklist_line_ids), 1)
        task.tag_ids = [(4, self.tag.id)]
        task.action_generate_qa_checklist()
        self.assertEqual(
            task.qa_checklist_line_ids.template_id,
            self.tmpl_general | self.tmpl_tagged,
        )
