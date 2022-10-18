# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tools
from odoo.models import trigger_tree_merge


def get_field_dependencies_tree(model_obj, fnames):
    """
    Returns a tree of all dependant fields,
    that will be triggered to recompute if fnames are modified.
    See ``modified`` of models.py
    """
    if len(fnames) == 1:
        tree = model_obj.pool.field_triggers.get(model_obj._fields[next(iter(fnames))])
    else:
        # merge dependency trees to evaluate all triggers at once
        tree = {}
        for fname in fnames:
            node = model_obj.pool.field_triggers.get(model_obj._fields[fname])
            if node:
                trigger_tree_merge(tree, node)
    return tree


@tools.ormcache("values")
def get_written_computed_fields(model_obj, values):
    """
    Returns field names tuple of written and computed fields
    """
    task_computed = tuple()
    tree = get_field_dependencies_tree(model_obj, values)
    if tree:
        tocompute = (
            model_obj.sudo().with_context(active_test=False)._modified_triggers(tree)
        )
        for field, _records, _create in tocompute:
            if field.model_name == model_obj._name:
                task_computed += (field.name,)
    return values + task_computed
