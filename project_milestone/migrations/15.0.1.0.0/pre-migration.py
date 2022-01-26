from openupgradelib import openupgrade

namespec = [("project_milestone", "project_task_milestone")]

field_spec = [
    ("project", "project_milestone", "target_date", "deadline"),
]


@openupgrade.migrate()
def migrate(cr, env, version):
    openupgrade.update_module_names(cr, namespec, False)
    openupgrade.rename_fields(cr, field_spec, False)
