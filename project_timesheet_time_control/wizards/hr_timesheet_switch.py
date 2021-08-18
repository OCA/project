# Copyright 2019 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrTimesheetSwitch(models.TransientModel):
    _name = "hr.timesheet.switch"
    _inherit = "account.analytic.line"
    _description = "Helper to quickly switch between timesheet lines"

    running_timer_id = fields.Many2one(
        comodel_name="account.analytic.line",
        string="Previous timer",
        ondelete="cascade",
        readonly=True,
        default=lambda self: self._default_running_timer_id(),
        help="This timer is running and will be stopped",
    )
    running_timer_start = fields.Datetime(
        string="Previous timer start",
        related="running_timer_id.date_time",
        readonly=True,
    )
    running_timer_duration = fields.Float(
        string="Previous timer duration",
        compute="_compute_running_timer_duration",
        help="When the previous timer is stopped, it will save this duration.",
    )
    # Redefine the relation to avoid using the same table than parent model
    tag_ids = fields.Many2many(relation="hr_timesheet_switch_line_tag_rel")

    @api.model
    def _default_running_timer_id(self, employee=None):
        """Obtain running timer."""
        employee = employee or self.env.user.employee_ids
        # Find running work
        running = self.env["account.analytic.line"].search(
            [
                ("date_time", "!=", False),
                ("employee_id", "in", employee.ids),
                ("id", "not in", self.env.context.get("resuming_lines", [])),
                ("project_id", "!=", False),
                ("unit_amount", "=", 0),
            ]
        )
        if len(running) > 1:
            raise UserError(
                _(
                    "%d running timers found. Cannot know which one to stop. "
                    "Please stop them manually."
                )
                % len(running)
            )
        return running

    @api.depends("date_time", "running_timer_id")
    def _compute_running_timer_duration(self):
        """Compute duration of running timer when stopped."""
        for one in self:
            one.running_timer_duration = one._duration(
                one.running_timer_id.date_time,
                one.date_time,
            )

    @api.model
    def _closest_suggestion(self):
        """Find most similar account.analytic.line record."""
        try:
            active = self.env[self.env.context["active_model"]].browse(
                self.env.context["active_id"]
            )
        except KeyError:
            # If I don't know where's the user, I don't know what to suggest
            return self.env["account.analytic.line"].browse()
        # If you're browsing another account.analytic.line, that's the match
        if active._name == "account.analytic.line":
            return active
        # If browsing other models, prepare a search
        domain = [("employee_id", "in", self.env.user.employee_ids.ids)]
        if active._name == "project.task":
            domain.append(("task_id", "=", active.id))
        elif active._name == "project.project":
            domain += [
                ("project_id", "=", active.id),
                ("task_id", "=", False),
            ]
        else:
            # No clues for other records, sorry
            return self.env["account.analytic.line"].browse()
        return self.env["account.analytic.line"].search(
            domain,
            order="date_time DESC",
            limit=1,
        )

    @api.model
    def default_get(self, fields_list):
        """Return defaults depending on the context where it is called."""
        result = super().default_get(fields_list)
        inherited = self._closest_suggestion()
        assert inherited._name == "account.analytic.line"
        # Inherit all possible fields from that account.analytic.line record
        if inherited:
            # Convert inherited to RPC-style values
            _fields = set(fields_list) & set(inherited._fields) - {
                # These fields must always be reset
                "id",
                "amount",
                "date_time",
                "date_time_end",
                "date",
                "is_task_closed",
                "unit_amount",
                # This field is from sale_timesheet, which is not among
                # this module dependencies; ignoring it will let you
                # resume an invoiced AAL if that module is installed,
                # and it doesn't hurt here
                "timesheet_invoice_id",
                # These fields are from the hr_timesheet_activity_begin_end
                # module. Unless ignored, these fields will cause a validation
                # error because time_stop - time_start must equal duration.
                "time_start",
                "time_stop",
            }
            inherited.read(_fields)
            values = inherited._convert_to_write(inherited._cache)
            for field in _fields:
                result[field] = values[field]
        return result

    def action_switch(self):
        """Stop old timer, start new one."""
        self.ensure_one()
        # Stop old timer
        self.with_context(
            resuming_lines=self.ids,
            stop_dt=self.date_time,
        ).running_timer_id.button_end_work()
        # Start new timer
        _fields = self.env["account.analytic.line"]._fields.keys()
        self.read(_fields)
        values = self._convert_to_write(self._cache)
        new = self.env["account.analytic.line"].create(
            {field: value for (field, value) in values.items() if field in _fields}
        )
        # Display created timer record if requested
        if self.env.context.get("show_created_timer"):
            form_view = self.env.ref("hr_timesheet.hr_timesheet_line_form")
            return {
                "res_id": new.id,
                "res_model": new._name,
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "view_type": "form",
                "views": [(form_view.id, "form")],
            }
        # Close wizard and reload view
        return {
            "type": "ir.actions.act_multi",
            "actions": [
                {"type": "ir.actions.act_window_close"},
                {"type": "ir.actions.act_view_reload"},
            ],
        }
