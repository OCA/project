def post_init_set_scoped_tags(cr, registry):
    """
    After module installation, ensure that every tag already used
    by a project or its tasks is listed in the 'available_in_project_ids'
    of that tag for the corresponding project.
    This keeps tag access consistent with existing usage.
    """

    from odoo.api import SUPERUSER_ID, Environment

    env = Environment(cr, SUPERUSER_ID, {})

    # Iterate over all projects
    projects = env["project.project"].search([])
    for project in projects:
        # Tags already on projects are directly assigned to the project
        # Let's add Tags assigned to tasks of the project
        tasks = env["project.task"].search([("project_id", "=", project.id)])
        for task in tasks:
            for tag in task.tag_ids:
                if project not in tag.available_in_project_ids:
                    tag.available_in_project_ids = [(4, project.id)]
