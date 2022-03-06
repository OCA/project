from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _timesheet_domain_get_invoiced_lines(self, sale_line_delivery):
        domain = super(AccountInvoiceLine, self)._timesheet_domain_get_invoiced_lines(
            sale_line_delivery
        )
        # invoice timesheet lines with duration
        # (or without duration and without start date, thus not to be stopped)
        return [
            "&",
            "|",
            ("unit_amount", "!=", "0"),
            "&",
            ("unit_amount", "=", "0"),
            ("date_time", "=", False),
        ] + domain
