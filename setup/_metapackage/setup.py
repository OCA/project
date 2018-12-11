import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-project_category',
        'odoo11-addon-project_department',
        'odoo11-addon-project_description',
        'odoo11-addon-project_key',
        'odoo11-addon-project_stage_closed',
        'odoo11-addon-project_stage_state',
        'odoo11-addon-project_task_add_very_high',
        'odoo11-addon-project_task_code',
        'odoo11-addon-project_task_default_stage',
        'odoo11-addon-project_task_dependency',
        'odoo11-addon-project_task_material',
        'odoo11-addon-project_task_material_stock',
        'odoo11-addon-project_task_pull_request',
        'odoo11-addon-project_task_send_by_mail',
        'odoo11-addon-project_timeline',
        'odoo11-addon-project_timeline_critical_path',
        'odoo11-addon-project_timeline_hr_timesheet',
        'odoo11-addon-project_timeline_task_dependency',
        'odoo11-addon-project_timesheet_time_control',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
