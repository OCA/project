import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-project_department',
        'odoo10-addon-project_description',
        'odoo10-addon-project_double_alias',
        'odoo10-addon-project_gtd',
        'odoo10-addon-project_issue_code',
        'odoo10-addon-project_issue_timesheet_time_control',
        'odoo10-addon-project_model_to_task',
        'odoo10-addon-project_parent',
        'odoo10-addon-project_recalculate',
        'odoo10-addon-project_stage_closed',
        'odoo10-addon-project_stage_state',
        'odoo10-addon-project_task_add_very_high',
        'odoo10-addon-project_task_category',
        'odoo10-addon-project_task_code',
        'odoo10-addon-project_task_default_stage',
        'odoo10-addon-project_task_dependency',
        'odoo10-addon-project_task_material',
        'odoo10-addon-project_task_material_analytic_partner',
        'odoo10-addon-project_task_material_stock',
        'odoo10-addon-project_task_pull_request',
        'odoo10-addon-project_timeline',
        'odoo10-addon-project_timesheet_currency',
        'odoo10-addon-project_timesheet_time_control',
        'odoo10-addon-project_wbs',
        'odoo10-addon-sale_order_project',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
