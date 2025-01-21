def set_project_ok_for_consumable_products(env):
    env["product.template"].search([("type", "=", "consu")]).write({"project_ok": True})
