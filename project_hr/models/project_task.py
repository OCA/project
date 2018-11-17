# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Linked employee",
        compute="_compute_employee_id",
        store=True,
    )
    hr_category_ids = fields.Many2many(
        comodel_name="hr.employee.category",
        string="Employee Categories",
        domain="[('id', 'in', allowed_hr_category_ids)]",
        help="Here you can select the employee category suitable to perform "
             "this task, limiting the selectable users to be assigned to "
             "those that belongs to that category.",
    )
    user_id = fields.Many2one(
        domain="[('id', 'in', allowed_user_ids)]",
    )
    allowed_hr_category_ids = fields.Many2many(
        comodel_name="hr.employee.category",
        string="Allowed HR categories",
        compute="_compute_allowed_hr_category_ids",
        help="Technical field for computing allowed employee categories "
             "according categories at project level.",
    )
    allowed_user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Allowed users",
        compute="_compute_allowed_user_ids",
        help="Technical field for computing allowed users according employee "
             "category.",
    )

    @api.depends('user_id', 'company_id')
    def _compute_employee_id(self):
        for task in self.filtered('user_id'):
            task.employee_id = task.user_id.employee_ids.filtered(
                lambda x: x.company_id == task.company_id
            )[:1]

    @api.depends('project_id', 'project_id.hr_category_ids')
    def _compute_allowed_hr_category_ids(self):
        hr_category_obj = self.env['hr.employee.category']
        for task in self:
            if task.project_id.hr_category_ids:
                task.allowed_hr_category_ids = task.project_id.hr_category_ids
            else:
                task.allowed_hr_category_ids = hr_category_obj.search([])

    @api.depends('hr_category_ids', 'company_id')
    def _compute_allowed_user_ids(self):
        user_obj = self.env['res.users']
        for task in self:
            domain = []
            if task.hr_category_ids:
                domain = [
                    ('employee_ids.company_id', '=', task.company_id.id),
                    ('employee_ids.category_ids', 'in',
                     task.hr_category_ids.ids),
                ]
            task.allowed_user_ids = user_obj.search(domain)

    @api.constrains('hr_category_ids', 'user_id')
    def _check_employee_category_user(self):
        """Check user's employee belong to the selected category."""
        for task in self.filtered(lambda x: x.hr_category_ids and x.user_id):
            if (any(x not in task.employee_id.category_ids
                    for x in task.hr_category_ids)):
                raise exceptions.ValidationError(
                    _("You can't assign a user not belonging to the selected "
                      "employee category."),
                )

    @api.constrains('hr_category_ids', 'project_id')
    def _check_employee_category_project(self):
        for task in self.filtered('hr_category_ids'):
            if (task.project_id.hr_category_ids and
                    bool(task.hr_category_ids -
                         task.project_id.hr_category_ids)):
                raise exceptions.ValidationError(
                    _("You can't assign a category that is not allowed at "
                      "project level."),
                )
