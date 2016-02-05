# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models

class EarnedValueTaskGraphs(models.TransientModel):
    _name = "earned.value.task.graphs"
    _description = "Earned Value Graphs"

    project_id = fields.Many2one('project.project',
                                 'Project', required=True)

    @api.multi
    def earned_value_graphs_open_window(self):
        """
        Opens Earned Value report
        """
        self.ensure_one()
        # Update the project EVM
        records = self.project_id.update_project_evm()

        return {
            'domain': "[('id','in', ["+','.join(map(str, records))+"])]",
            'name': _('Earned Value Records'),
            'view_type': 'form',
            'view_mode': 'graph,tree,form',
            'res_model': 'project.evm.task',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }

