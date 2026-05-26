# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    auto_done_days = fields.Integer(
        string="Auto-mark as done after days",
        default=0,
        help="Automatically mark tasks as done after staying in this stage "
        "for the specified number of days. Set to 0 to disable this feature.",
    )

    allow_done_from_in_progress = fields.Boolean(
        string="Allow Done from In Progress",
        default=False,
    )

    allow_done_from_changes_requested = fields.Boolean(
        string="Allow Done from Changes Requested",
        default=False,
    )

    allow_done_from_approved = fields.Boolean(
        string="Allow Done from Approved",
        default=False,
    )

    allow_done_from_waiting = fields.Boolean(
        string="Allow Done from Waiting",
        default=False,
    )

    auto_cancel_days = fields.Integer(
        string="Auto-cancel after days",
        default=0,
        help="Automatically cancel tasks after staying in this stage "
        "for the specified number of days. Set to 0 to disable this feature.",
    )

    allow_cancel_from_in_progress = fields.Boolean(
        string="Allow Cancel from In Progress",
        default=False,
    )

    allow_cancel_from_changes_requested = fields.Boolean(
        string="Allow Cancel from Changes Requested",
        default=False,
    )

    allow_cancel_from_approved = fields.Boolean(
        string="Allow Cancel from Approved",
        default=False,
    )

    allow_cancel_from_waiting = fields.Boolean(
        string="Allow Cancel from Waiting",
        default=False,
    )

    _auto_done_days_non_negative_check = models.Constraint(
        "CHECK(auto_done_days >= 0)",
        "Auto Done days must be non-negative.",
    )
    _auto_cancel_days_non_negative_check = models.Constraint(
        "CHECK(auto_cancel_days >= 0)",
        "Auto Cancel days must be non-negative.",
    )

    def _get_auto_x_allowed_states(self, done_or_cancel):
        """Return the allowed states for the given action.

        Args:
            done_or_cancel (str): The action to be performed ['done', 'cancel']

        Returns:
            list: The allowed states for the given action.
        """
        self.ensure_one()
        allowed_states = []
        if getattr(self, f"allow_{done_or_cancel}_from_in_progress"):
            allowed_states.append("01_in_progress")
        if getattr(self, f"allow_{done_or_cancel}_from_changes_requested"):
            allowed_states.append("02_changes_requested")
        if getattr(self, f"allow_{done_or_cancel}_from_approved"):
            allowed_states.append("03_approved")
        if getattr(self, f"allow_{done_or_cancel}_from_waiting"):
            allowed_states.append("04_waiting_normal")
        return allowed_states

    @api.constrains(
        "auto_done_days",
        "allow_done_from_in_progress",
        "allow_done_from_changes_requested",
        "allow_done_from_approved",
        "allow_done_from_waiting",
    )
    def _check_auto_done_states(self):
        """Check if the auto-done days are set and if at least one state
        is selected to allow marking as done."""
        for stage in self:
            if stage.auto_done_days > 0:
                if not stage._get_auto_x_allowed_states("done"):
                    raise ValidationError(
                        self.env._(
                            "When 'Auto-mark as done after days' is set for stage "
                            "'%(stage)s', at least one state must be selected "
                            "to allow marking as done.",
                            stage=stage.name,
                        )
                    )

    @api.constrains(
        "auto_cancel_days",
        "allow_cancel_from_in_progress",
        "allow_cancel_from_changes_requested",
        "allow_cancel_from_approved",
        "allow_cancel_from_waiting",
    )
    def _check_auto_cancel_states(self):
        """Check if the auto-cancel days are set and if at least one state
        is selected to allow auto-cancel."""
        for stage in self:
            if stage.auto_cancel_days > 0:
                if not stage._get_auto_x_allowed_states("cancel"):
                    raise ValidationError(
                        self.env._(
                            "When 'Auto-cancel after days' is set for stage "
                            "'%(stage)s', at least one state must be selected "
                            "to allow auto-cancel.",
                            stage=stage.name,
                        )
                    )
