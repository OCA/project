{
    "name": "Project Task Stage Order",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow",
    "summary": "Allows each project to have its own task stage order",
    "category": "Project",
    "depends": ["project_task_stage_mgmt"],
    "data": [
        "security/ir.model.access.csv",
        "security/project_task_type_sequence_security.xml",
        "views/project_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "post_init_hook": "post_init_hook",
}
