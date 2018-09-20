# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string="Employees",
    )


class Task(models.Model):
    _inherit = 'project.task'

    employee_ids = fields.Many2many(
        compute='_compute_employee_ids',
        comodel_name='hr.employee',
        string="Employees",
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Assigned to employee",
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
    def _compute_employee_ids(self):
        for record in self:
            emp = record.mapped('project_id.employee_ids')
            skills = record.employee_category_id
            if skills:
                emp = emp.filtered(lambda r: skills & r.category_ids)
            record.employee_ids = emp.ids

    @api.multi
    @api.depends('employee_id', 'date_start',
                 'date_end')
    def _compute_scheduled(self):
        for rec in self:
            start, stop = rec.date_start, rec.date_end
            rec.scheduled = rec.employee_id and start and stop

    @api.onchange('project_id')
    def _onchange_project_id_employee_id(self):
        return {
            'domain': {
                'employee_id': [('id', 'in', self.project_id.employee_ids.ids)]
            }
        }
