# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    code = fields.Char(string='Sequence', copy=False)

    _sql_constraints = [
        ('unique_sequence', 'UNIQUE (code)',
         _('The sequence must be unique!')),
    ]

    @api.model
    def create(self, data):
        if not data.get('code'):
            seq_obj = self.env['ir.sequence']
            seq = seq_obj.next_by_code('sequence.project.task')
            data['code'] = seq
        return super(ProjectTask, self).create(data)
