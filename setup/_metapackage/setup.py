import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-project_category',
        'odoo14-addon-project_deadline',
        'odoo14-addon-project_key',
        'odoo14-addon-project_list',
        'odoo14-addon-project_milestone',
        'odoo14-addon-project_parent_task_filter',
        'odoo14-addon-project_role',
        'odoo14-addon-project_stage_closed',
        'odoo14-addon-project_stage_state',
        'odoo14-addon-project_status',
        'odoo14-addon-project_stock_request',
        'odoo14-addon-project_tag',
        'odoo14-addon-project_task_add_very_high',
        'odoo14-addon-project_task_code',
        'odoo14-addon-project_task_default_stage',
        'odoo14-addon-project_task_dependency',
        'odoo14-addon-project_task_material',
        'odoo14-addon-project_task_pull_request',
        'odoo14-addon-project_template',
        'odoo14-addon-project_timeline',
        'odoo14-addon-project_timeline_task_dependency',
        'odoo14-addon-project_timesheet_time_control',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
