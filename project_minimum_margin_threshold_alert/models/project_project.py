# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

from odoo.addons.base.models.res_users import ResUsers


class ProjectProject(models.Model):
    _inherit = "project.project"

    margin_threshold = fields.Float(
        help="Percentage of project costs compared to project revenues "
        "that triggers an alert",
        default=lambda self: self._default_margin_threshold,
        tracking=True,
    )
    is_margin_threshold_exceeded = fields.Boolean(
        help="This is set if margin is exceeded from threshold",
        tracking=True,
    )
    is_margin_threshold_exceeded_notfication_sent = fields.Boolean(
        compute="_compute_is_margin_threshold_exceeded_notfication_sent",
        store=True,
        index=True,
        tracking=True,
    )
    force_margin_threshold_notification = fields.Boolean(
        string="Force email notification sending (margin)",
        default=lambda self: self._default_force_margin_threshold_notification,
        help="Check this if you want to send emails when margin is exceeded.",
    )
    create_margin_threshold_activity = fields.Boolean(
        default=lambda self: self._default_create_margin_threshold_activity,
        help="Check this in order to create activities for users "
        "with that parameter activated when margin threshold is exceeded.",
    )

    @property
    def _default_margin_threshold(self):
        return float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_margin_threshold_alert.project_margin_threshold")
        )

    @property
    def _default_force_margin_threshold_notification(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "project_margin_threshold_alert.project_margin_threshold_send_email"
            )
        )

    @property
    def _default_create_margin_threshold_activity(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "project_margin_threshold_alert.project_margin_threshold_create_activity"
            )
        )

    def _get_margin_threshold_to_notify_domain(self) -> list:
        """
        Build the domain to get projects that need to notify
        partners and users about margin threshold exceed.
        """
        return [
            ("is_margin_threshold_exceeded_notfication_sent", "=", False),
            ("is_margin_threshold_exceeded", "=", True),
        ]

    def _cron_margin_threshold_exceeded(self) -> None:
        """
        This method will:
            - Update the field 'is_margin_threshold_exceeded'
            - Notify users
        """
        projects = self.env["project.project"].search([])  # pylint: disable=no-search-all
        projects._update_is_margin_threshold_exceeded()
        for project in projects.filtered_domain(
            self._get_margin_threshold_to_notify_domain()
        ):
            users_to_notify = project._get_internal_users_for_margin_threshold()
            project._send_margin_threshold_notifications(users_to_notify)

            if project.force_margin_threshold_notification:
                project._post_message_to_partners(users_to_notify.partner_id)

            if project.create_margin_threshold_activity:
                project._create_margin_threshold_activity_for_manager(project.user_id)
        projects.is_margin_threshold_exceeded_notfication_sent = True

    def _send_margin_threshold_notifications(self, users_to_notify):
        self.message_notify(
            partner_ids=users_to_notify.filtered(
                lambda u: u.receive_project_margin_threshold_notification
            ).partner_id.ids,
            body=f"Cost threshold exceeded for project {self.name}!",
            subject="Project Cost Threshold Exceeded",
            email_layout_xmlid=None,
        )

    def _update_is_margin_threshold_exceeded(self):
        """
        Update the field "is_margin_threshold_exceeded"
        Do it asynchronously as the mean to compute it depends on
        additionnal modules that fill in the "_get_margin_items"
        method -> not possible to do it with compute/depends triggers.
        """
        for project in self:
            margin_values, _show = project._get_profitability_values()
            margin = float(margin_values.get("expected_percentage", "0"))
            # Margin is set to 0 if no costs. Ignore it
            project.is_margin_threshold_exceeded = bool(
                margin and ((margin / 100) < project.margin_threshold)
            )

    def _post_message_to_partners(self, partners):
        template = (
            "project_minimum_margin_threshold_alert."
            "project_minimum_margin_exceeded_template"
        )
        self.message_post_with_source(source_ref=template, partner_ids=partners.ids)

    def _create_margin_threshold_activity_for_manager(self, manager):
        if manager:
            self.env["mail.activity"].create(
                {
                    "res_model_id": self.env["ir.model"]._get_id("project.project"),
                    "res_id": self.id,
                    "user_id": manager.id,
                    "activity_type_id": self.env.ref(
                        "project_minimum_margin_threshold_alert.mail_activity_type_margin_threshold"
                    ).id,
                }
            )

    def _get_internal_users_for_margin_threshold(self) -> ResUsers:
        """
        Returns the internal followers and the project manager (user_id)
        """
        internal_user_followers = (
            self.message_partner_ids.user_ids.filtered(lambda x: not x.share)
            | self.user_id
        )
        return internal_user_followers

    @api.depends("margin_threshold")
    def _compute_is_margin_threshold_exceeded_notfication_sent(self):
        """
        Threshold has been changed -> reset the notification is sent field
        """
        self.is_margin_threshold_exceeded_notfication_sent = False
