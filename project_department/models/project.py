# © 2014 Joël Grand-Guillaume (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    project_department_id = fields.Many2one(
        related='project_id.department_id',
        string='Project Department',
        store=True
    )


class Project(models.Model):
    _name = "project.project"
    _description = "Project"
    _inherit = ['mail.alias.mixin', 'mail.thread', 'portal.mixin']
    _inherits = {'account.analytic.account': "analytic_account_id"}

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        required=True,
        ondelete='restrict'
    )
