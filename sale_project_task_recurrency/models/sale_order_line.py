# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta

from odoo import fields, models

MONTH_NB_TASK_MAPPING = {
    "month": 1,
    "quarter": 3,
    "semester": 6,
    "year": 12,
}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_task_prepare_values(self, project):
        values = super()._timesheet_create_task_prepare_values(project)
        if self.product_id.recurring_task:
            repeat_type = (
                "until"
                if self.product_id.task_repeat_type == "repeat"
                else self.product_id.task_repeat_type
            )
            repeat_unit = (
                "month"
                if self.product_id.task_repeat_unit in ["quarter", "semester"]
                else self.product_id.task_repeat_unit
            )
            repeat_interval = self.product_id.task_repeat_interval
            if self.product_id.task_repeat_unit == "quarter":
                repeat_interval *= 3
            elif self.product_id.task_repeat_unit == "semester":
                repeat_interval *= 6
            date_deadline = self._get_task_date_deadline()
            values.update(
                {
                    "repeat_interval": repeat_interval,
                    "repeat_unit": repeat_unit,
                    "repeat_type": repeat_type,
                    "recurring_task": True,
                    "date_deadline": date_deadline,
                    "repeat_until": self._get_task_repeat_until(date_deadline),
                }
            )
        return values

    def _get_task_date_deadline(self):
        self.ensure_one()
        product = self.product_id
        date_now = fields.Datetime.context_timestamp(self, datetime.now())
        task_start_date_method = product.task_start_date_method
        # Initial deadline based on current date and time
        date_deadline = date_now.replace(hour=12, minute=0, second=0)
        forced_month = int(product.task_force_month or 0)
        if product.task_repeat_unit in ["quarter", "semester"]:
            forced_month = int(
                product[f"task_force_month_{product.task_repeat_unit}"] or 0
            )
        month_period = month = date_deadline.month
        month_nb = MONTH_NB_TASK_MAPPING.get(product.task_repeat_unit) or 0
        if product.task_repeat_unit in ["quarter", "semester", "year"]:
            month_nb = MONTH_NB_TASK_MAPPING[product.task_repeat_unit]
            # The period number is started by 0 to be able to calculate the month
            period_number = (month - 1) // month_nb
            if product.task_repeat_unit == "year":
                month_period = 1
            elif product.task_repeat_unit != "month":
                # Checking quarterly and semesterly
                month_period = period_number * month_nb + 1
            if product.task_repeat_unit != "month" and forced_month:
                # When the selected period is year, the period_number field is
                # 0, so forced_month will take the value of the forced month set
                # on product.
                forced_month = month_nb * period_number + forced_month
        if (
            forced_month
            and product.task_repeat_unit in ["quarter", "semester", "year"]
            and task_start_date_method == "current_date"
        ):
            date_deadline += relativedelta(month=forced_month)
        if (
            product.task_repeat_unit in ["month", "quarter", "semester", "year"]
            and task_start_date_method != "current_date"
        ):
            is_end = "end_" in task_start_date_method
            # If forced_month is set, use it, but if it isn't use the month_period
            date_deadline += relativedelta(day=1, month=forced_month or month_period)
            if is_end:
                increment = month_nb - 1 if not forced_month else 0
                date_deadline += relativedelta(months=increment, day=31)
            if "_next" in task_start_date_method:
                date_deadline += relativedelta(
                    months=month_nb * product.task_repeat_interval
                )
                if is_end:
                    date_deadline += relativedelta(day=31)
        return date_deadline.astimezone(pytz.UTC).replace(tzinfo=None)

    def _get_task_repeat_until(self, date_start):
        self.ensure_one()
        product = self.product_id
        repeat_until = False
        if product.task_repeat_type == "repeat":
            if product.task_repeat_unit == "month":
                repeat_until = date_start + relativedelta(
                    months=product.task_repeat_number * product.task_repeat_interval
                )
            else:
                force_month = (
                    int(product.task_force_month) if product.task_force_month else 0
                )
                repeat_until = date_start + relativedelta(
                    years=product.task_repeat_number * product.task_repeat_interval,
                    month=force_month or None,
                )
        elif product.task_repeat_type == "until":
            repeat_until = product.task_repeat_until
        return repeat_until
