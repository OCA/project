# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Domatix Technologies  S.L. (http://www.domatix.com)
#                       info <info@domatix.com>
#                        Angel Moya <angel.moya@domatix.com>
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

from openerp import fields, models, api


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.one
    def _get_department_ids(self):
        employees = self.env['hr.employee'].search([('user_id', '=', self.id)])
        self.department_ids = self.env['hr.department']
        for employee in employees:
            self.department_ids |= employee.department_id

    department_ids = fields.Many2many(
        comodel_name='hr.department',
        relation='user_department_rel',
        column1='user_id',
        column2='department_id',
        compute=_get_department_ids)
