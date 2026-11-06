# Copyright 2026 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from markupsafe import Markup

from odoo import _, api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    qa_checklist_line_ids = fields.One2many(
        comodel_name="project.task.qa.checklist.line",
        inverse_name="task_id",
        string="QA Checklist",
    )
    qa_checklist_progress = fields.Char(
        compute="_compute_qa_checklist_progress",
    )
    qa_checklist_state = fields.Selection(
        selection=[
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("complete", "Complete"),
            ("complete_with_failures", "Complete with Failures"),
        ],
        compute="_compute_qa_checklist_progress",
    )
    is_qa_stage = fields.Boolean(
        related="stage_id.is_qa_stage",
        string="In QA Stage",
    )
    qa_evidence_ids = fields.Many2many(
        comodel_name="ir.attachment",
        string="QA Evidence",
    )
    qa_evidence_url = fields.Char(
        string="QA Evidence Link",
        help="External evidence link (e.g. a screen recording on Drive/Loom). "
        "Preferred over attaching heavy video files to the database.",
    )

    @api.depends("qa_checklist_line_ids.state")
    def _compute_qa_checklist_progress(self):
        for task in self:
            lines = task.qa_checklist_line_ids
            total = len(lines)
            reviewed = lines.filtered(lambda line: line.state != "pending")
            done = len(reviewed)
            if not total:
                task.qa_checklist_progress = False
                task.qa_checklist_state = "not_started"
                continue
            percent = round(done * 100 / total)
            task.qa_checklist_progress = f"{done}/{total} ({percent}%)"
            if done < total:
                task.qa_checklist_state = "not_started" if not done else "in_progress"
            elif reviewed.filtered(lambda line: line.state == "failed"):
                task.qa_checklist_state = "complete_with_failures"
            else:
                task.qa_checklist_state = "complete"

    def write(self, vals):
        if "stage_id" not in vals:
            return super().write(vals)
        new_stage = self.env["project.task.type"].browse(vals["stage_id"])
        leaving_qa = self.filtered(
            lambda task: task.stage_id.is_qa_stage and not new_stage.is_qa_stage
        )
        res = super().write(vals)
        if new_stage.is_qa_stage:
            self.action_generate_qa_checklist()
        for task in leaving_qa:
            task._qa_notify_incomplete()
        return res

    def action_generate_qa_checklist(self):
        """Create the checklist lines that apply to each task, idempotently."""
        templates = self.env["project.task.qa.checklist.template"].search([])
        line_model = self.env["project.task.qa.checklist.line"]
        for task in self:
            existing = task.qa_checklist_line_ids.template_id
            task_tags = task.tag_ids
            applicable = templates.filtered(
                lambda tmpl, tags=task_tags: tmpl.always_applicable
                or (tmpl.tag_ids & tags)
            )
            to_create = applicable - existing
            vals_list = [task._prepare_qa_checklist_line(t) for t in to_create]
            if vals_list:
                line_model.create(vals_list)
        return True

    def _prepare_qa_checklist_line(self, template):
        self.ensure_one()
        return {
            "task_id": self.id,
            "template_id": template.id,
            "sequence": template.sequence,
            "name": template.name,
        }

    def _qa_incomplete_lines(self):
        self.ensure_one()
        return self.qa_checklist_line_ids.filtered(
            lambda line: line.state in ("pending", "failed")
        )

    def _qa_missing_evidence(self):
        self.ensure_one()
        return not self.qa_evidence_ids and not self.qa_evidence_url

    def _qa_notify_incomplete(self):
        """Warn (never block) when leaving a QA stage with an open checklist
        or without any evidence loaded."""
        self.ensure_one()
        lines = self._qa_incomplete_lines()
        missing_evidence = self._qa_missing_evidence()
        if not lines and not missing_evidence:
            return
        items = Markup("").join(
            Markup("<li>%s (%s)</li>") % (line.name, line.state) for line in lines
        )
        if missing_evidence:
            items += Markup("<li>%s</li>") % _("No QA evidence loaded")
        body = Markup("%s<ul>%s</ul>") % (
            _("This task left a QA stage with:"),
            items,
        )
        self.message_post(
            body=body,
            partner_ids=self.user_ids.partner_id.ids,
        )
        manager = self.project_id.user_id
        if manager:
            self.activity_schedule(
                act_type_xmlid="project_task_qa_checklist."
                "mail_activity_qa_checklist_review",
                summary=_("Review QA checklist"),
                note=body,
                user_id=manager.id,
            )
