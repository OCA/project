# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2014 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
#                 Endika Iglesias <endikaig@antiun.com>
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
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    workday_begin = fields.Float(string="Workday Begin", default=8.0)
    workday_end = fields.Float(string="Workday End", default=17.0)

    @api.one
    @api.constrains('workday_begin')
    def _check_workday_begin(self):
        if self.workday_begin < 0.0 or self.workday_begin > 23.0:
            raise ValidationError(_('Workday Begin value must be between '
                                    '00:00 and 23:00'))

    @api.one
    @api.constrains('workday_end')
    def _check_workday_end(self):
        if self.workday_end < 1.0 or self.workday_end >= 24.0:
            raise ValidationError(_('Workday End value must be between '
                                    '01:00 and 23:59'))
