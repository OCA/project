# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Task(models.Model):
    _inherit = 'project.task'

    employee_domain_ids = fields.Many2many(
        compute='_compute_employee_domain_ids',
        comodel_name='hr.employee',
        string="Employees",
    )
    employee_scheduling_ids = fields.Many2many(
        compute='_compute_employee_scheduling_ids',
        comodel_name='hr.employee',
        string="Employees",
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Assigned to employee",
        domain="[('id', 'in', employee_domain_ids)]",
    )
    employee_category_id = fields.Many2one(
        comodel_name='hr.employee.category',
        string="Employee category",
    )
    scheduled = fields.Boolean(
        compute='_compute_scheduled',
        readonly=True,
        store=True,
    )

    @api.multi
    @api.depends('project_id.employee_ids.category_ids',
                 'employee_category_id')
    def _compute_employee_domain_ids(self):
        for record in self:
            emp = record.mapped('project_id.employee_ids')
            task_skill = record.employee_category_id
            if task_skill:
                emp = emp.filtered(lambda r: task_skill in r.category_ids)
            record.employee_domain_ids = emp.ids

    @api.multi
    @api.depends('project_id.employee_ids.category_ids',
                 'employee_category_id')
    def _compute_employee_scheduling_ids(self):
        for record in self:
            employees = record.employee_id
            if record.date_end or not record.employee_id:
                employees = record.employee_domain_ids
            record.employee_scheduling_ids = employees

    @api.multi
    @api.depends('employee_id', 'date_start', 'date_end')
    def _compute_scheduled(self):
        for record in self:
            record.scheduled = record.date_end

    @api.onchange('employee_domain_ids')
    def _onchange_employee_domain_ids(self):
        if self.employee_id not in self.employee_domain_ids:
            self.employee_id = False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.user_id != self.employee_id.user_id:
            self.user_id = self.employee_id.user_id
