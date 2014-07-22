# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Daniel Reis
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

from openerp.osv import orm
from openerp import SUPERUSER_ID


class ProjectTask(orm.Model):
    _inherit = 'project.task'

    def message_post(
            self, cr, uid, thread_id, body='', subject=None,
            type='notification', subtype=None, parent_id=False,
            attachments=None, context=None, content_subtype='html', **kwargs):
        """ Overrides mail_thread message_post so that we can write messages
            on read only documents.
        """
        return super(ProjectTask, self).message_post(
            cr, SUPERUSER_ID,
            thread_id, body=body, subject=subject, type=type, subtype=subtype,
            parent_id=parent_id, attachments=attachments, context=context,
            content_subtype=content_subtype, **kwargs)
