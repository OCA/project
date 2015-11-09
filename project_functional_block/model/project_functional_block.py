# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Akretion LDTA (<http://www.akretion.com>).
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class ProjectFunctionalBlock(models.Model):
    _name = 'project.functional.block'
    _description = 'Functional block to organize projects tasks'
    _order = 'complete_name'
    _rec_name = 'complete_name'

    # Columns
    name = fields.Char('Name', size=64, required=True, translate=True)
    code = fields.Char('Code', size=8)
    # TODO: this field doesn't work with multi-languages
    complete_name = fields.Char(string="Complete Name", index=True)
    description = fields.Text('Description', translate=True)
    parent_id = fields.Many2one(
        'project.functional.block', 'Parent Block',
        ondelete='cascade', index=True)
    tasks_count = fields.Integer(string='Tasks Count', compute='_count_tasks')
    child_fblocks_count = fields.Integer(
        string='Child Blocks Count', compute='_count_child_fblocks')

    @api.multi
    def _update_complete_name(self):
        """
        Complete Name includes parent's name and name of this functional block
        itself.
        """
        todo_fblocks = self.search([('id', 'child_of', self.ids)],
                                   order='complete_name')
        for func_block in todo_fblocks:
            complete_name = func_block.name
            parent = func_block.parent_id
            while parent:
                complete_name = parent.name + ' / ' + complete_name
                parent = parent.parent_id
            func_block.complete_name = complete_name

    @api.model
    def create(self, vals):
        new_fblock = super(ProjectFunctionalBlock, self).create(vals)
        # Update complete_name for this record
        if 'updating_complete_name' not in self._context:
            ctx = self._context.copy()
            ctx.update({'updating_complete_name': True})
            new_fblock.with_context(ctx)._update_complete_name()
        return new_fblock

    @api.multi
    def write(self, vals):
        res = super(ProjectFunctionalBlock, self).write(vals)
        # Update complete_name for these records and child records
        if 'updating_complete_name' not in self._context:
            ctx = self._context.copy()
            ctx.update({'updating_complete_name': True})
            self.with_context(ctx)._update_complete_name()
        return res

    @api.multi
    def _count_tasks(self):
        """
        Count the number of tasks of given functional block(s).
        """
        task_obj = self.env['project.task']
        for fblock in self:
            tasks_count = task_obj.search(
                [('functional_block_id', '=', fblock.id)], count=True)
            fblock.tasks_count = tasks_count

    @api.multi
    def action_view_tasks(self):
        """
        View tasks of the given block.
        """
        self.ensure_one()
        action = self.env.ref('project.action_view_task')
        task_obj = self.env['project.task']
        tasks = task_obj.search([('functional_block_id', '=', self.id)])
        ret_ctx = {
            'default_functional_block_id': self.id
        }
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': str(ret_ctx),
            'res_model': action.res_model,
            'domain': "[('id', 'in', (" + ','.join(map(str, tasks.ids))
            + ",))]"
        }

    @api.multi
    def _count_child_fblocks(self):
        """
        Count the number of child blocks of given functional block(s).
        """
        for fblock in self:
            child_fblocks_count = self.search(
                [('id', 'child_of', fblock.id), ('id', '!=', fblock.id)],
                count=True)
            fblock.child_fblocks_count = child_fblocks_count

    @api.multi
    def action_view_child_fblocks(self):
        """
        View child blocks of the given block.
        """
        self.ensure_one()
        action = self.env.ref(
            'project_functional_block.action_funct_block_list')
        child_fblocks = self.search(
            [('id', 'child_of', self.id), ('id', '!=', self.id)])
        ret_ctx = {
            'default_parent_id': self.id
        }
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': str(ret_ctx),
            'res_model': action.res_model,
            'domain': "[('id', 'in', (" + ','.join(map(str, child_fblocks.ids))
            + ",))]"
        }
