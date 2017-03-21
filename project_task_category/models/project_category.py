# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class ProjectCategory(models.Model):
    _name = 'project.category.main'
    _inherit = 'project.category'
