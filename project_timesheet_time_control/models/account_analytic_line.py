# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order = 'date_time desc, id desc'

    date_time = fields.Datetime(
        default=fields.Datetime.now,
        copy=False,
    )
    show_time_control = fields.Selection(
        selection=[("resume", "Resume"), ("stop", "Stop")],
        compute="_compute_show_time_control",
        help="Indicate which time control button to show, if any.",
    )

    @api.model
    def _eval_date(self, vals):
        if vals.get('date_time'):
            return dict(vals, date=fields.Date.from_string(vals['date_time']))
        return vals

    @api.model
    def _running_domain(self):
        """Domain to find running timesheet lines."""
        return [
            ("date_time", "!=", False),
            ("employee_id", "in", self.env.user.employee_ids.ids),
            ("project_id.allow_timesheets", "=", True),
            ("unit_amount", "=", 0),
        ]

    @api.model
    def _duration(self, start, end):
        """Compute float duration between start and end."""
        if isinstance(start, str):
            start = fields.Datetime.from_string(start)
        if isinstance(end, str):
            end = fields.Datetime.from_string(end)

        if not (start and end):
            return 0

        try:
            return (end - start).total_seconds() / 3600
        except TypeError:
            _logger.warning("Cannot compute duration", exc_info=True)
            return 0

    @api.depends("employee_id", "unit_amount")
    def _compute_show_time_control(self):
        """Decide when to show time controls."""
        for one in self:
            if one.employee_id not in self.env.user.employee_ids:
                one.show_time_control = False
            elif one.unit_amount or not one.date_time:
                one.show_time_control = "resume"
            else:
                one.show_time_control = "stop"

    @api.model
    def create(self, vals):
        return super().create(self._eval_date(vals))

    @api.multi
    def write(self, vals):
        return super().write(self._eval_date(vals))

    def button_resume_work(self):
        """Create a new record starting now, with a running timer."""
        return {
            "name": _("Resume work"),
            "res_model": "hr.timesheet.switch",
            "target": "new",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
        }

    @api.multi
    def button_end_work(self):
        end = fields.Datetime.from_string(
            self.env.context.get("stop_dt", fields.Datetime.now()))
        for line in self:
            if line.unit_amount:
                raise UserError(
                    _("Cannot stop timer %d because it is not running. "
                      "Refresh the page and check again.") %
                    line.id
                )
            date = fields.Datetime.from_string(line.date_time)
            line.unit_amount = line._duration(date, end)
        return True
