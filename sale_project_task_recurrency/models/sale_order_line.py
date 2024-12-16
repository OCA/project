# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta

from odoo import fields, models


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
            date_deadline = self._get_task_date_deadline()
            values.update(
                {
                    "repeat_interval": self.product_id.task_repeat_interval,
                    "repeat_unit": self.product_id.task_repeat_unit,
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
        force_month = int(product.task_force_month) if product.task_force_month else 0
        task_start_date_method = product.task_start_date_method
        date_deadline_tz = fields.Datetime.context_timestamp(
            self, datetime.now()
        ) + relativedelta(hour=12, minute=0, second=0)
        if (
            force_month
            and product.task_repeat_unit == "year"
            and task_start_date_method == "current_date"
        ):
            date_deadline_tz += relativedelta(month=force_month)
        date_deadline = date_deadline_tz.astimezone(pytz.UTC).replace(tzinfo=None)
        if (
            product.task_repeat_unit in ["month", "year"]
            and task_start_date_method != "current_date"
        ):
            if product.task_repeat_unit == "month":
                date_deadline += relativedelta(day=1)
                if "_next" in task_start_date_method:
                    date_deadline += relativedelta(months=product.task_repeat_interval)
                if "end_" in task_start_date_method:
                    date_deadline += relativedelta(day=31)
            else:
                date_deadline += relativedelta(month=force_month or 1, day=1)
                if "_next" in task_start_date_method:
                    date_deadline += relativedelta(years=product.task_repeat_interval)
                if "end_" in task_start_date_method:
                    date_deadline += relativedelta(month=force_month or 12, day=31)
        return date_deadline

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
