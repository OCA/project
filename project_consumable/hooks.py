# Copyright 2021-2025 - Pierre Verkest
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def set_project_ok_for_consumable_products(env):
    env["product.template"].search([("type", "=", "consu")]).write({"project_ok": True})
