# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    costs_threshold = fields.Float(
        help="Percentage of project costs compared to project revenues "
        "that triggers an alert",
        compute="_compute_costs_threshold",
        store=True,
        readonly=False,
    )
    is_cost_exceeded_cost_threshold = fields.Boolean(
        compute="_compute_is_cost_exceeded_cost_threshold", default=False, store=True
    )
    is_notfication_sent_cost_threshold = fields.Boolean(default=False)
    force_notification_send_cost_threshold = fields.Boolean(
        string="Force mail notification send", default=False
    )
    create_activity = fields.Boolean(default=False)

    @api.depends("company_id")
    def _compute_costs_threshold(self):
        for project in self:
            project.costs_threshold = project.company_id.project_costs_threshold

    def _cron_find_costs_threshold_exceeded(self):
        projects = self.env["project.project"].search([()])
        for project in projects:
            project._compute_is_cost_exceeded_cost_threshold()
            if (
                project.is_cost_exceeded_cost_threshold
                and not project.is_notfication_sent_cost_threshold
            ):
                users_to_notify = project._get_internal_users()
                project._send_notifications(users_to_notify)
                project._send_notifications(users_to_notify)

                if project.force_notification_send_cost_threshold:
                    project._post_message_to_partners(users_to_notify.partner_id)

                if project.create_activity:
                    project._create_activity_for_manager(project.user_id)
                project.is_notfication_sent_cost_threshold = True

    def _send_notifications(self, users_to_notify):
        self.message_notify(
            partner_ids=users_to_notify.filtered(
                lambda u: u.receive_project_threshold_notification
            ).partner_id.ids,
            body=f"Cost threshold exceeded for project {self.name}!",
            subject="Project Cost Threshold Exceeded",
            email_layout_xmlid=None,
        )

    @api.depends("costs_threshold", "company_id.project_costs_threshold")
    def _compute_is_cost_exceeded_cost_threshold(self):
        for project in self:
            profitability_items = project._get_profitability_items(with_action=False)

            total_costs_billed = profitability_items["costs"]["total"]["billed"]
            total_costs_to_bill = profitability_items["costs"]["total"]["to_bill"]
            total_costs_expected = total_costs_billed + total_costs_to_bill

            total_revenues_invoiced = profitability_items["revenues"]["total"][
                "invoiced"
            ]
            total_revenues_to_invoice = profitability_items["revenues"]["total"][
                "to_invoice"
            ]
            total_revenues_expected = (
                total_revenues_invoiced + total_revenues_to_invoice
            )

            costs_threshold = (
                project.costs_threshold or project.company_id.project_costs_threshold
            )
            costs_exceeded = (total_costs_expected * -1) > (
                total_revenues_expected * costs_threshold
            )
            project.is_cost_exceeded_cost_threshold = costs_exceeded

    def _post_message_to_partners(self, partners):
        template = (
            "project_profitability_threshold_alert.project_costs_exceeded_template"
        )
        self.message_post_with_source(source_ref=template, partner_ids=partners.ids)

    def _create_activity_for_manager(self, manager):
        if manager:
            self.env["mail.activity"].create(
                {
                    "res_model_id": self.env["ir.model"]._get_id("project.project"),
                    "res_id": self.id,
                    "user_id": manager.id,
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "summary": "Project Cost Threshold Exceeded",
                }
            )

    def _get_internal_users(self):
        manager = self.user_id
        internal_user_followers = self.message_partner_ids.user_ids.filtered(
            lambda x: not x.share
        )
        if manager and manager not in internal_user_followers:
            internal_user_followers += manager
        return internal_user_followers

    @api.onchange("costs_threshold")
    def _reset_is_notfication_sent_cost_threshold(self):
        self._origin.is_notfication_sent_cost_threshold = False
