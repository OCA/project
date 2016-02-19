# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

_KPI_TYPE = [('PV', 'Planned Value'),
             ('EV', 'Earned Value'),
             ('AC', 'Actual Cost'),
             ('CV', 'Cost Variance'),
             ('CVP', 'Cost Variance Percent'),
             ('CPI', 'Cost Performance Index'),
             ('TCPI', 'To-Complete Cost Performance Index'),
             ('SV', 'Schedule Variance'),
             ('SVP', 'Schedule Variance Percent'),
             ('SPI', 'Schedule Performance Index'),
             ('EAC', 'Estimate at Completion'), 
             ('ETC', 'Estimate to Complete'),
             ('VAC', 'Variance at Completion'),
             ('VACP', 'Variance at Completion Percent'),
             ('BAC', 'Budget at Completion'),
             ('PCC', 'Costs to date / Total costs'),
             ('POC', '% Complete')]


class ProjectEvmTask(models.Model):

    _name = 'project.evm.task'
    _description = 'Project Earned Value Management indicators'

    name = fields.Char('Title', size=64, required=False)
    date = fields.Date('Date')
    eval_date = fields.Char('Printed Date', size=64, required=True)
    kpi_type = fields.Selection(_KPI_TYPE, 'Type', required=True,)
    project_id = fields.Many2one('project.project', 'Project',
                                 ondelete='cascade')
    kpi_value = fields.Float('Value')
