from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    xml_ids = [
        "project_task_default_stage.project_tt_analysis",
        "project_task_default_stage.project_tt_specification",
        "project_task_default_stage.project_tt_design",
        "project_task_default_stage.project_tt_development",
        "project_task_default_stage.project_tt_testing",
        "project_task_default_stage.project_tt_merge",
        "project_task_default_stage.project_tt_deployment",
        "project_task_default_stage.project_tt_cancel",
    ]
    for xml_id in xml_ids:
        task_type = env.ref(xml_id, raise_if_not_found=False)
        if task_type:
            task_type.user_id = False
