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
    _order = 'parent_id desc, name'
    _rec_name = 'complete_name'
    _parent_store = True
    _parent_order = 'name'

    # Columns
    name = fields.Char('Name', size=64, required=True, translate=True)
    code = fields.Char('Code', size=8)
    complete_name = fields.Char(
        string='Complete Name', compute='_compute_complete_name')
    description = fields.Text('Description', translate=True)
    parent_id = fields.Many2one(
        'project.functional.block', 'Parent Block',
        ondelete='cascade', index=True)
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)
    tasks_count = fields.Integer(string='Tasks Count', compute='_count_tasks')
    child_fblocks_count = fields.Integer(
        string='Child Blocks Count', compute='_count_child_fblocks')

    @api.multi
    def _compute_complete_name(self):
        """
        Complete Name includes parent's name and name of this functional block
        itself.
        """
        todo_fblocks = self.search([('id', 'child_of', self.ids)],
                                   order='parent_id desc, name')
        for func_block in todo_fblocks:
            complete_name = func_block.name
            parent = func_block.parent_id
            while parent:
                complete_name = parent.name + ' / ' + complete_name
                parent = parent.parent_id
            func_block.complete_name = complete_name

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
        task_ids_str = ','.join(map(str, tasks.ids))
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
            'domain': "[('id', 'in', (" + task_ids_str + ",))]"
        }

    @api.multi
    def _count_child_fblocks(self):
        """
        Count the number of child blocks of given functional block(s).
        """
        for fblock in self:
            child_fblocks_count = self.search_count(
                [('id', 'child_of', fblock.id), ('id', '!=', fblock.id)])
            fblock.child_fblocks_count = child_fblocks_count
            # Test
            fcount = 0
            block_lst = [fblock]
            while block_lst:
                current_block = block_lst.pop()
                child_blocks = self.search(
                    [('parent_id', '=', current_block.id)])
                if not child_blocks:
                    continue
                fcount += len(child_blocks)
                block_lst += child_blocks

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
        child_fblock_ids_str = child_fblocks and\
            ','.join(map(str, child_fblocks.ids)) or\
            '-1'
        ret_ctx = {'default_parent_id': self.id}
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': str(ret_ctx),
            'res_model': action.res_model,
            'domain': "[('id', 'in', (" + child_fblock_ids_str + ",))]"
        }
