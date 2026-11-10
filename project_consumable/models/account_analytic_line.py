# Copyright 2021-2025 - Pierre Verkest
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    consumable_project_id = fields.Many2one(
        "project.project",
        domain='[("allow_consumables", "=", True)]',
        string="Project (consumable)",
    )

    @api.depends("consumable_project_id.partner_id", "account_id.partner_id")
    def _compute_partner_id(self):
        res = super()._compute_partner_id()
        for consumable in self:
            if consumable.consumable_project_id:
                consumable.partner_id = (
                    consumable.consumable_project_id.partner_id
                    or consumable.account_id.partner_id
                )
        return res

    def _consumable_preprocess_create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") and "consumable_project_id" in vals:
                vals["name"] = "/"
        return vals_list

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = self._consumable_preprocess(vals_list)
        vals_list = self._consumable_preprocess_create(vals_list)

        lines = super().create(vals_list)

        for line, values in zip(lines, vals_list, strict=False):
            if line.consumable_project_id:
                line._consumable_postprocess(values)
        return lines

    def write(self, values):
        values = self._consumable_preprocess([values])[0]
        result = super().write(values)
        self.filtered(lambda t: t.consumable_project_id)._consumable_postprocess(values)
        return result

    def _consumable_preprocess(self, vals_list):
        """Deduce other field values from the one given.
        Override this to compute on the fly some field that can not be computed fields.
        :param values: dict values for `create`or `write`.
        """
        for vals in vals_list:
            if all(v in vals for v in ["product_id", "consumable_project_id"]):
                if "product_uom_id" not in vals:
                    product = (
                        self.env["product.product"].sudo().browse(vals["product_id"])
                    )
                    vals["product_uom_id"] = product.uom_id.id
            if not vals.get("account_id") and "consumable_project_id" in vals:
                account = (
                    self.env["project.project"]
                    .browse(vals["consumable_project_id"])
                    .analytic_account_id
                )
                if not account or not account.active:
                    raise ValidationError(
                        _(
                            "Materials must be created on a project "
                            "with an active analytic account."
                        )
                    )
                vals["account_id"] = account.id
        return vals_list

    def _consumable_postprocess(self, values):
        sudo_self = self.sudo()
        values_to_write = self._consumable_postprocess_values(values)
        for consumable in sudo_self:
            if values_to_write[consumable.id]:
                consumable.write(values_to_write[consumable.id])
        return values

    def _consumable_postprocess_values(self, values):
        """Get the additional values to write on record
        :param dict values: values for the model's fields, as a dictionary::
            {'field_name': field_value, ...}
        :return: a dictionary mapping each record id to its corresponding
            dictionary values to write (may be empty).
        """
        result = {id_: {} for id_ in self.ids}
        sudo_self = self.sudo()

        if any(
            field_name in values
            for field_name in [
                "unit_amount",
                "product_id",
                "product_uom_id",
                "date",
            ]
        ):
            for material in sudo_self:
                if material.consumable_project_id and material.product_id:
                    cost = material.product_id.standard_price or 0.0
                    qty = material.unit_amount
                    if (
                        material.product_uom_id
                        and material.product_id.uom_id
                        and material.product_uom_id != material.product_id.uom_id
                    ):
                        qty = material.product_uom_id._compute_quantity(
                            qty,
                            material.product_id.uom_id,
                        )
                    amount = -1 * qty * cost
                    amount_converted = material.product_id.currency_id._convert(
                        amount,
                        material.account_id.currency_id,
                        self.env.company,
                        material.date,
                    )
                    result[material.id].update(
                        {
                            "amount": amount_converted,
                        }
                    )
        return result
