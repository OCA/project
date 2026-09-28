# Copyright 2021-2025 - Pierre Verkest
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, _lt, api, fields, models
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = "project.project"

    allow_consumables = fields.Boolean(
        "Consumable", default=False, help="Project allowed while collecting consumable"
    )
    consumable_ids = fields.One2many(
        "account.analytic.line", "consumable_project_id", "Associated Consumables"
    )
    consumable_count = fields.Integer(
        compute="_compute_consumable_total_price",
        compute_sudo=True,
        help="Number of consumable lines collected.",
    )
    consumable_total_price = fields.Monetary(
        compute="_compute_consumable_total_price",
        help="Total price of all consumables recorded in the project.",
        compute_sudo=True,
        currency_field="currency_id",
    )

    @api.constrains("allow_consumables", "analytic_account_id")
    def _check_allow_consumables(self):
        for project in self:
            if project.allow_consumables and not project.analytic_account_id:
                raise ValidationError(
                    _("You cannot use consumables without an analytic account.")
                )

    @api.depends(
        "consumable_ids",
        "consumable_ids.amount",
        "consumable_ids.consumable_project_id",
    )
    def _compute_consumable_total_price(self):
        consumables_read_group = self.env["account.analytic.line"]._read_group(
            [("consumable_project_id", "in", self.ids)],
            ["consumable_project_id"],
            ["consumable_project_id:count", "amount:sum"],
        )
        self.consumable_total_price = 0
        self.consumable_count = 0
        for project, count, amount_sum in consumables_read_group:
            project.consumable_total_price = amount_sum
            project.consumable_count = count

    def action_project_consumable(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "project_consumable.consumable_action_report_by_project"
        )
        action["display_name"] = _("%(name)s's Materials", name=self.name)
        action["domain"] = [("consumable_project_id", "in", self.ids)]
        return action

    def _get_stat_buttons(self):
        buttons = super()._get_stat_buttons()
        if not self.allow_consumables or not self.env.user.has_group(
            "project.group_project_manager"
        ):
            return buttons

        buttons.append(
            {
                "icon": "copy",
                "text": _lt("Materials"),
                "number": _lt(
                    "%(amount)s %(currency_symbol)s (%(count)s)",
                    amount=self.consumable_total_price,
                    count=self.consumable_count,
                    currency_symbol=self.currency_id.symbol,
                ),
                "action_type": "object",
                "action": "action_project_consumable",
                "show": True,
                "sequence": 6,
            }
        )
        return buttons
