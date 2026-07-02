# Copyright 2026 Patryk Pyczko (Nagarro)<patryk.pyczko@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import calendar

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date


class Project(models.Model):
    _inherit = "project.project"

    postsale_active = fields.Boolean(string="Activate Post-sale", tracking=True)
    postsale_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Post-sale Responsible",
        domain="[('share', '=', False), ('sale_team_id', '!=', False)]",
        ondelete="restrict",
        help="Internal user responsible for the generated post-sale "
        "leads (must have a Sales Team assigned).",
    )
    postsale_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Post-sale Customer",
        help="Customer assigned to the generated leads. Defaults "
        "to the project customer.",
    )
    postsale_interval = fields.Integer(string="Interval", default=1)
    postsale_rule = fields.Selection(
        [
            ("days", _("Days")),
            ("weeks", _("Weeks")),
            ("months", _("Months")),
            ("quarters", _("Quarters")),
            ("semesters", _("Semesters")),
            ("years", _("Years")),
        ],
        string="Unit",
        default="months",
    )
    postsale_day_of_month = fields.Integer(
        string="Day of Month",
        default=1,
        help="Day of the month to generate the opportunity (1-31). If the month "
        "has fewer days, the last day of that month will be used.",
    )
    postsale_name_template = fields.Char(
        string="Name Template",
        default="{period_label} {year} - {project_name}",
        help="Allowed variables: {project_name}, {period_label}, {year}",
    )
    postsale_generate_tags = fields.Boolean(
        string="Generate CRM Tags",
        default=True,
        help="Automatically create and assign a tag like 'Q2 2026 "
        "- Postsale' to the lead.",
    )
    postsale_notes = fields.Html(
        string="Internal Notes",
        help="Internal notes or description that will propagate directly "
        "into the generated CRM Lead description.",
    )
    postsale_last_date = fields.Date(string="Last Generation Date")
    postsale_next_date = fields.Date(string="Next Generation Date")

    postsale_next_executions = fields.Html(
        string="Next Executions Preview", compute="_compute_postsale_next_executions"
    )
    postsale_lead_count = fields.Integer(
        compute="_compute_postsale_lead_count", string="Post-sale Leads"
    )

    def _get_postsale_configuration_error(self):
        """Returns an error string if configuration is invalid, else False."""
        self.ensure_one()
        if self.postsale_interval <= 0:
            return _("Periodicity must be greater than 0.")

        if self.postsale_rule in ["months", "quarters", "semesters", "years"] and (
            self.postsale_day_of_month < 1 or self.postsale_day_of_month > 31
        ):
            return _("Day of month must be between 1 and 31.")

        if self.postsale_name_template:
            try:
                self.postsale_name_template.format(
                    project_name="Test", period_label="Q1", year=2026
                )
            except (ValueError, KeyError, IndexError):
                return _(
                    "Invalid Name Template syntax. Please check your "
                    "brackets {} and use only allowed variables:"
                    "{project_name}, {period_label}, {year}."
                )

        return False

    @api.constrains(
        "postsale_active",
        "postsale_user_id",
        "postsale_interval",
        "postsale_rule",
        "postsale_day_of_month",
        "postsale_name_template",
    )
    def _check_postsale_configuration(self):
        for rec in self:
            if not rec.postsale_active:
                continue

            if not rec.postsale_user_id:
                raise UserError(_("Please set a Post-sale Responsible."))

            error_msg = rec._get_postsale_configuration_error()
            if error_msg:
                raise UserError(error_msg)

    @api.onchange("postsale_active", "partner_id")
    def _onchange_postsale_active(self):
        """Pre-fill the post-sale customer in real-time when tracking is activated."""
        if not self.postsale_partner_id and self.partner_id:
            self.postsale_partner_id = self.partner_id

    def _compute_postsale_lead_count(self):
        lead_data = (
            self.env["crm.lead"]
            .sudo()
            ._read_group(
                domain=[("project_id", "in", self.ids), ("is_postsale", "=", True)],
                groupby=["project_id"],
                aggregates=["__count"],
            )
        )
        mapped_data = {project.id: count for project, count in lead_data}
        for project in self:
            project.postsale_lead_count = mapped_data.get(project.id, 0)

    @api.depends(
        "postsale_active",
        "postsale_next_date",
        "postsale_interval",
        "postsale_rule",
        "postsale_day_of_month",
        "postsale_name_template",
    )
    def _compute_postsale_next_executions(self):
        for rec in self:
            if not rec.postsale_active or not rec.postsale_next_date:
                rec.postsale_next_executions = _(
                    "<p class='text-muted'>Not active or missing next date.</p>"
                )
                continue

            error_msg = rec._get_postsale_configuration_error()
            if error_msg:
                rec.postsale_next_executions = _(
                    "<p class='text-danger'><b>⚠️ Configuration Error:</b> "
                    "%(error_msg)s</p>",
                    error_msg=error_msg,
                )
                continue

            html = "<ul>"
            current_date = rec.postsale_next_date
            for _i in range(5):
                period_label = rec._get_period_label(current_date)
                name = rec._format_postsale_name(current_date, period_label)
                formatted_date = format_date(self.env, current_date)
                html += f"<li><strong>{formatted_date}:</strong> {name}</li>"
                current_date = rec._calculate_next_date(current_date)
            html += "</ul>"
            rec.postsale_next_executions = html

    def write(self, vals):
        """Override to log in chatter when activated/deactivated"""
        res = super().write(vals)
        if "postsale_active" in vals:
            for rec in self:
                if rec.postsale_active:
                    # Fetch the translated labels dictionary for the selection field
                    rule_labels = dict(
                        rec._fields["postsale_rule"]._description_selection(rec.env)
                    )
                    translated_rule = rule_labels.get(
                        rec.postsale_rule, rec.postsale_rule
                    )

                    rec.message_post(
                        body=_(
                            "Post-sale tracking ACTIVATED. Interval: "
                            "%(interval)s %(rule)s.",
                            interval=rec.postsale_interval,
                            rule=translated_rule,
                        )
                    )
                else:
                    rec.message_post(body=_("Post-sale tracking DEACTIVATED."))
        return res

    def _calculate_next_date(self, base_date):
        self.ensure_one()
        interval = self.postsale_interval
        rule = self.postsale_rule

        if rule == "days":
            return base_date + relativedelta(days=interval)
        elif rule == "weeks":
            return base_date + relativedelta(weeks=interval)

        months_to_add = 0
        if rule == "months":
            months_to_add = interval
        elif rule == "quarters":
            months_to_add = interval * 3
        elif rule == "semesters":
            months_to_add = interval * 6
        elif rule == "years":
            months_to_add = interval * 12

        next_date = base_date + relativedelta(months=months_to_add)
        target_day = self.postsale_day_of_month
        max_day = calendar.monthrange(next_date.year, next_date.month)[1]
        safe_day = min(target_day, max_day)

        return next_date.replace(day=safe_day)

    def _get_period_label(self, target_date):
        """Helper to get the string representation of the period (e.g., 'Q2', 'W32')"""
        rule = self.postsale_rule
        period_label = ""

        if rule == "days":
            period_label = _("Day %s", target_date.strftime("%d"))
        elif rule == "weeks":
            period_label = _("W%s", target_date.isocalendar()[1])
        elif rule == "months":
            period_label = format_date(
                self.env, target_date, date_format="MMMM"
            ).capitalize()
        elif rule == "quarters":
            quarter = (target_date.month - 1) // 3 + 1
            period_label = _("Q%s", quarter)
        elif rule == "semesters":
            semester = 1 if target_date.month <= 6 else 2
            period_label = _("S%s", semester)
        elif rule == "years":
            period_label = _("Annual")

        return period_label

    def _format_postsale_name(self, target_date, period_label):
        self.ensure_one()
        template = self.postsale_name_template or "{project_name}"
        try:
            name = template.format(
                project_name=self.name, period_label=period_label, year=target_date.year
            )
        except Exception:
            name = f"{period_label} {target_date.year} - {self.name}"

        return name

    def _get_postsale_tags(self, target_date, period_label):
        """Generates or retrieves the CRM tags for the post-sale lead."""
        self.ensure_one()
        if not self.postsale_generate_tags:
            return []

        tag_format = _("%(period)s %(year)s - Postsale")
        tag_name = tag_format % {
            "period": period_label,
            "year": target_date.year,
        }

        tag = self.env["crm.tag"].search([("name", "=", tag_name)], limit=1)
        if not tag:
            tag = self.env["crm.tag"].create({"name": tag_name})

        return [(4, tag.id, 0)]

    def _prepare_postsale_lead_vals(self, target_date):
        """Prepares the dictionary to create the CRM Lead."""
        self.ensure_one()
        period_label = self._get_period_label(target_date)
        lead_name = self._format_postsale_name(target_date, period_label)

        return {
            "name": lead_name,
            "type": "opportunity",
            "user_id": self.postsale_user_id.id,
            "team_id": self.postsale_user_id.sale_team_id.id or False,
            "partner_id": self.postsale_partner_id.id or self.partner_id.id or False,
            "project_id": self.id,
            "is_postsale": True,
            "postsale_cycle_date": target_date,
            "expected_revenue": 0.0,
            "tag_ids": self._get_postsale_tags(target_date, period_label),
            "description": self.postsale_notes,
        }

    def action_generate_postsale_opportunity(self):
        """Creates the opportunity. Called by Cron and Debug button."""
        self.ensure_one()
        if not self.postsale_active or not self.postsale_next_date:
            return

        target_date = self.postsale_next_date

        existing_lead = self.env["crm.lead"].search(
            [
                ("project_id", "=", self.id),
                ("is_postsale", "=", True),
                ("postsale_cycle_date", "=", target_date),
            ],
            limit=1,
        )

        if existing_lead:
            # If exists, skip creation but push date forward to heal the timeline
            self.postsale_last_date = target_date
            self.postsale_next_date = self._calculate_next_date(target_date)
            return

        lead_vals = self._prepare_postsale_lead_vals(target_date)
        self.env["crm.lead"].create(lead_vals)

        self.postsale_last_date = target_date
        self.postsale_next_date = self._calculate_next_date(target_date)

    @api.model
    def _cron_generate_postsale_opportunities(self):
        """Cron entry point - Safe, isolated and logging-focused."""
        today = fields.Date.today()
        projects = self.search(
            [("postsale_active", "=", True), ("postsale_next_date", "<=", today)]
        )
        for project in projects:
            try:
                with self.env.cr.savepoint():
                    project.action_generate_postsale_opportunity()
            except Exception as e:
                self.env["ir.logging"].sudo().create(
                    {
                        "name": "Post-sale Cron",
                        "type": "server",
                        "level": "ERROR",
                        "dbname": self.env.cr.dbname,
                        "message": (
                            "Error generating postsale for project "
                            f"{project.id}: {str(e)}"
                        ),
                        "func": "_cron_generate_postsale_opportunities",
                        "path": "project.py",
                        "line": "0",
                    }
                )

    def action_view_postsale_leads(self):
        self.ensure_one()
        return {
            "name": _("Post-sale Opportunities"),
            "view_mode": "tree,form",
            "res_model": "crm.lead",
            "domain": [("project_id", "=", self.id), ("is_postsale", "=", True)],
            "type": "ir.actions.act_window",
            "context": {"default_project_id": self.id},
        }
