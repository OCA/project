from openupgradelib import openupgrade

xml_ids = ["project_task_form"]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, xml_ids)
    env.cr.execute(
        """
        INSERT INTO task_dependencies_rel(task_id, depends_on_id)
        SELECT task_id, dependency_task_id FROM project_task_dependency_task_rel;
        """
    )
    env.cr.execute(
        """
        UPDATE project_project SET allow_task_dependencies=true
        WHERE id in (SELECT project_id FROM project_task WHERE id in (SELECT task_id
        FROM project_task_dependency_task_rel));
        """
    )
