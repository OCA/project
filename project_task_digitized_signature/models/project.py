# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    signature = fields.Image(help="Signature", copy=False, attachment=True)
    is_signed = fields.Boolean(compute="_compute_is_signed")

    @api.depends("signature")
    def _compute_is_signed(self):
        for task in self:
            task.is_signed = task.signature

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if vals.get("signature"):
            for task in self:
                task._attach_sign()
        return res

    def _attach_sign(self):
        """Render the delivery report in pdf and attach it to the task in `self`."""
        self.ensure_one()
        report = self.env["ir.actions.report"]._render_qweb_pdf(
            "project_task_report.report_project_task_action", self.id
        )
        filename = "%s_signed_task_report" % self.name
        if self.partner_id:
            message = _("Task signed by %s") % (self.partner_id.name)
        else:
            message = _("Task signed")
        self.message_post(
            attachments=[("%s.pdf" % filename, report[0])],
            body=message,
        )
        return True
