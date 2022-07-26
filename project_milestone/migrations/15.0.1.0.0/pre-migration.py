from openupgradelib import openupgrade

namespec = [("project_milestone", "project_task_milestone")]

field_spec = [
    ("project.milestone", "project_milestone", "target_date", "deadline"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(env.cr, namespec, False)
    openupgrade.rename_fields(env, field_spec, False)
