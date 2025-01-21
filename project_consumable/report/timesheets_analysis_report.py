from odoo import api, models


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    @api.model
    def _where(self):
        where_clause = super()._where()
        where_clause += " AND A.product_id IS NULL"
        return where_clause
