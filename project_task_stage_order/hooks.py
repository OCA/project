def post_init_hook(env):
    env["project.task.type"].search([])._sync_task_stage_order()
    company = env.ref("base.main_company")
    env.ref(
        "project_task_stage_order.project_task_type_sequence_comp_rule"
    ).sudo().domain_force = f"[('company_id', 'in', [{company.id}, False])]"
