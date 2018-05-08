# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [('project.category.main', 'project.category'), ]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    try:
        openupgrade.lift_constraints(cr, 'project_task', 'categ_id')
        openupgrade.lift_constraints(cr, 'business_requirement_resource_template', 'categ_id')
        openupgrade.lift_constraints(cr, 'business_requirement_resource', 'categ_id')
        openupgrade.rename_tables(cr, [('project_category_main', 'project_category'), ])
        openupgrade.rename_models(cr, _model_renames)
        #print "project_category /  business_requirement_resource upgrade done. "
    except Exception, e:
        raise e

