# Copyright 2022 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ForecastLine(models.Model):

    _inherit = "forecast.line"

    @api.model
    def _read_group_raw(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        """
        Inherit and add __range key, like in odoo 15
        https://github.com/odoo/odoo/blob/15.0/odoo/models.py#L2431
        """
        result = super()._read_group_raw(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        dt = [
            f
            for f in groupby
            if self._fields[f.split(":")[0]].type
            in ("date", "datetime")  # e.g. 'date:month'
        ]
        for group in result:
            if dt:
                group["__range"] = {}
            for df in dt:
                field_name = df.split(":")[0]
                if group.get(df):
                    range_from, range_to = group[df][0].split("/")
                    group["__range"][field_name] = {"from": range_from, "to": range_to}
                    # Inject another date key in the result
                    # for easier retrieval later on
                    group["forecast_date_start"] = range_from
                else:
                    group["__range"][field_name] = False
                    group["forecast_date_start"] = False
        return result
