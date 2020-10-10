import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-project_category',
        'odoo13-addon-project_description',
        'odoo13-addon-project_hr',
        'odoo13-addon-project_key',
        'odoo13-addon-project_list',
        'odoo13-addon-project_milestone',
        'odoo13-addon-project_parent_task_filter',
        'odoo13-addon-project_purchase_link',
        'odoo13-addon-project_role',
        'odoo13-addon-project_stage_closed',
        'odoo13-addon-project_stage_state',
        'odoo13-addon-project_status',
        'odoo13-addon-project_tag',
        'odoo13-addon-project_task_add_very_high',
        'odoo13-addon-project_task_code',
        'odoo13-addon-project_task_default_stage',
        'odoo13-addon-project_task_dependency',
        'odoo13-addon-project_task_material',
        'odoo13-addon-project_task_pull_request',
        'odoo13-addon-project_task_send_by_mail',
        'odoo13-addon-project_template',
        'odoo13-addon-project_timeline',
        'odoo13-addon-project_timeline_hr_timesheet',
        'odoo13-addon-project_timeline_task_dependency',
        'odoo13-addon-project_timesheet_time_control',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
