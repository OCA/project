# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    recurring_task = fields.Boolean(string="Is recurring task?")
    task_repeat_interval = fields.Integer(string="Repeat Every", default=1)
    task_repeat_unit = fields.Selection(
        [
            ("day", "Days"),
            ("week", "Weeks"),
            ("month", "Months"),
            ("quarter", "Quarters"),
            ("semester", "Semesters"),
            ("year", "Years"),
        ],
        default="week",
    )
    task_repeat_type = fields.Selection(
        [
            ("forever", "Forever"),
            ("repeat", "Repeat"),
            ("until", "Until"),
        ],
        default="forever",
        string="Until",
    )
    task_repeat_number = fields.Integer(string="# Repeats", default=1)
    task_repeat_until = fields.Date(string="End Date")
    task_start_date_method = fields.Selection(
        [
            ("current_date", "Current date"),
            ("start_this", "Start of current period"),
            ("end_this", "End of current period"),
            ("start_next", "Start of next period"),
            ("end_next", "End of next period"),
        ],
        "Start Date Method",
        default="current_date",
        help="""This field allows to define how the start date of the task will
        be calculated:

        - Current date: The start date will be Current date.
        - Start of current period: The start date will be the first day of the actual
        period selected. Example: If we are on 2024/08/27
        and the period selected is 'Year(s)' the start date will be 2024/01/01.
        - End of current period: The start date will be the last day of the actual
        period selected. Example: If we are on 2024/08/27
        and the period selected is 'Year(s)' the start date will be 2024/12/31.
        - Start of next period: The start date will be the first day of the next
        period selected. Example: If we are on 2024/08/27
        and the period selected is 'Year(s)' the start date will be 2025/01/01.
        - End of next period: The start date will be the last day of the actual
        period selected. Example: If we are on 2024/08/27
        and the period selected is 'Year(s)' the start date will be 2025/12/31.
        """,
    )
    task_force_month = fields.Selection(
        [
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        "Force Month",
    )
    task_force_month_quarter = fields.Selection(
        [
            ("1", "First month"),
            ("2", "Second month"),
            ("3", "Third month"),
        ],
        "Force Month Quarter",
        help="Force the month to be used inside the quarter",
    )
    task_force_month_semester = fields.Selection(
        [
            ("1", "First month"),
            ("2", "Second month"),
            ("3", "Third month"),
            ("4", "Fourth month"),
            ("5", "Fifth month"),
            ("6", "Sixth month"),
        ],
        "Force Month Semester",
        help="Force the month to be used inside the semester",
    )

    @api.onchange("service_tracking")
    def _onchange_service_tracking(self):
        res = super()._onchange_service_tracking()
        if self.service_tracking not in ["task_global_project", "task_in_project"]:
            self.recurring_task = False
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("service_tracking")
    def _onchange_service_tracking(self):
        res = super()._onchange_service_tracking()
        if self.service_tracking not in ["task_global_project", "task_in_project"]:
            self.recurring_task = False
        return res
