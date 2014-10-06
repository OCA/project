# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camtocamp SA
# @author Joël Grand-Guillaume
# $Id: $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import orm, fields


class project_service_type(orm.Model):
    _name = "project.service_type"
    _description = "Service type"
    _columns = {
        'name': fields.char('Service Type', required=True, size=64),
    }


class project_project(orm.Model):
    _inherit = 'project.project'
    _columns = {
        'project_service_id': fields.many2one('project.service_type',
                                              'Service Type',
                                              required=True),
        'project_type': fields.selection(
            [('forfait', 'Forfait'),
                ('plafond', 'Plafond'),
                ('regie', 'Regie')], 'Type', required=True),
    }
