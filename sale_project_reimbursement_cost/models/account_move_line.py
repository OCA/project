from odoo import models
from odoo.tools import float_compare


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _sale_create_reinvoice_sale_line(self):
        """
        Generate an additional line in the sale order for the provision product
        only if the remaining amount in the provision product is greater than 0.
        - Sale lines with the same analytic account and reimbursement product.
        - Analytic lines with the same analytic account and provision product.
        """
        SaleLine = self.env["sale.order.line"]
        AnalyticLine = self.env["account.analytic.line"]
        map_sale_line_per_move = super()._sale_create_reinvoice_sale_line()
        for line in self.filtered(lambda aml: aml.product_id.provision_product_id):
            provision_product = line.product_id.provision_product_id
            sale_lines = map_sale_line_per_move.get(line.id) or []
            for sale_line in sale_lines:
                distribution_analytic_account_ids = (
                    sale_line.distribution_analytic_account_ids
                )
                provision_data = AnalyticLine._read_group(
                    [
                        ("account_id", "in", distribution_analytic_account_ids.ids),
                        ("product_id", "=", provision_product.id),
                    ],
                    groupby=["product_id"],
                    aggregates=["amount:sum"],
                )
                if not provision_data:
                    continue
                sale_reimbursement_data = SaleLine._read_group(
                    [
                        (
                            "distribution_analytic_account_ids",
                            "in",
                            distribution_analytic_account_ids.ids,
                        ),
                        ("product_id", "=", line.product_id.id),
                        ("id", "!=", sale_line.id),
                        ("is_expense", "=", True),
                    ],
                    groupby=["product_id"],
                    aggregates=["untaxed_amount_to_invoice:sum"],
                )
                reimbursement_amount = (
                    sale_reimbursement_data[0][1] if sale_reimbursement_data else 0.0
                )
                amount_remainig = max(provision_data[0][1] - reimbursement_amount, 0)
                amount = min(amount_remainig, line.price_subtotal)
                if (
                    float_compare(
                        amount, 0.0, precision_rounding=line.currency_id.rounding
                    )
                    <= 0
                ):
                    continue
                default_values = {
                    "product_id": provision_product.id,
                    "name": f"{line.name} ({provision_product.display_name})",
                    "price_unit": amount,
                    "product_uom_qty": -1,
                    "order_id": sale_line.order_id.id,
                    "is_expense": False,
                    "qty_invoiced": 1,
                }
                new_sale_line = sale_line.copy(default_values)
                new_sale_line.write(
                    {"analytic_distribution": sale_line.analytic_distribution or False}
                )
        return map_sale_line_per_move
