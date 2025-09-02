# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Linked employees",
        compute="_compute_employee_ids",
        store=True,
    )
    hr_category_ids = fields.Many2many(
        comodel_name="hr.employee.category",
        string="Employee Categories",
        domain="domain_hr_category_ids",
        help="Here you can select the employee category suitable to perform "
        "this task, limiting the selectable users to be assigned to "
        "those that belongs to that category.",
    )
    domain_hr_category_ids = fields.Binary(compute="_compute_domain_hr_category_ids")
    user_ids = fields.Many2many(domain="domain_user_ids")
    domain_user_ids = fields.Binary(compute="_compute_domain_user_ids")

    @api.depends("user_ids", "company_id")
    def _compute_employee_ids(self):
        for task in self.filtered("user_ids"):
            task.employee_ids = task.user_ids.employee_ids.filtered(
                lambda x, company_id=task.company_id or self.env.company: x.company_id
                == company_id
            )

    @api.depends("project_id", "project_id.hr_category_ids")
    def _compute_domain_hr_category_ids(self):
        for task in self:
            domain = []
            if task.project_id.hr_category_ids:
                domain = [("id", "in", task.project_id.hr_category_ids.ids)]
            task.domain_hr_category_ids = domain

    @api.depends("hr_category_ids", "company_id")
    def _compute_domain_user_ids(self):
        for task in self:
            domain = [("share", "=", False), ("active", "=", True)]
            if task.hr_category_ids:
                domain = [
                    (
                        "employee_ids.company_id",
                        "=",
                        (task.company_id.id or self.env.company.id),
                    ),
                    ("employee_ids.category_ids", "in", task.hr_category_ids.ids),
                ]
            task.domain_user_ids = domain

    @api.constrains("hr_category_ids", "user_ids")
    def _check_employee_category_user(self):
        """Check user's employee belong to the selected category."""
        for task in self.filtered(lambda x: x.hr_category_ids and x.user_ids):
            if any(
                x not in task.employee_ids.category_ids for x in task.hr_category_ids
            ):
                raise exceptions.ValidationError(
                    self.env._(
                        "You can't assign a user not belonging to the selected "
                        "employee category."
                    )
                )

    @api.constrains("hr_category_ids", "project_id")
    def _check_employee_category_project(self):
        for task in self.filtered("hr_category_ids"):
            if task.project_id.hr_category_ids and bool(
                task.hr_category_ids - task.project_id.hr_category_ids
            ):
                raise exceptions.ValidationError(
                    self.env._(
                        "You can't assign a category that is not allowed at "
                        "project level."
                    )
                )
