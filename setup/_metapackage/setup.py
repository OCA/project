import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-project_change_state',
        'odoo9-addon-project_closing',
        'odoo9-addon-project_department',
        'odoo9-addon-project_description',
        'odoo9-addon-project_double_alias',
        'odoo9-addon-project_issue_code',
        'odoo9-addon-project_issue_task',
        'odoo9-addon-project_issue_timesheet_time_control',
        'odoo9-addon-project_stage_closed',
        'odoo9-addon-project_stage_state',
        'odoo9-addon-project_task_add_very_high',
        'odoo9-addon-project_task_code',
        'odoo9-addon-project_task_default_stage',
        'odoo9-addon-project_task_delegate',
        'odoo9-addon-project_task_dependency',
        'odoo9-addon-project_task_digitized_signature',
        'odoo9-addon-project_task_materials',
        'odoo9-addon-project_task_materials_stock',
        'odoo9-addon-project_task_send_by_mail',
        'odoo9-addon-project_timeline',
        'odoo9-addon-project_timesheet_time_control',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
