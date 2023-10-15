import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-project_administrator_restricted_visibility>=15.0dev,<15.1dev',
        'odoo-addon-project_department>=15.0dev,<15.1dev',
        'odoo-addon-project_duplicate_subtask>=15.0dev,<15.1dev',
        'odoo-addon-project_forecast_line>=15.0dev,<15.1dev',
        'odoo-addon-project_forecast_line_bokeh_chart>=15.0dev,<15.1dev',
        'odoo-addon-project_forecast_line_holidays_public>=15.0dev,<15.1dev',
        'odoo-addon-project_hr>=15.0dev,<15.1dev',
        'odoo-addon-project_list>=15.0dev,<15.1dev',
        'odoo-addon-project_milestone>=15.0dev,<15.1dev',
        'odoo-addon-project_parent_task_filter>=15.0dev,<15.1dev',
        'odoo-addon-project_purchase_analytic_global>=15.0dev,<15.1dev',
        'odoo-addon-project_role>=15.0dev,<15.1dev',
        'odoo-addon-project_sequence>=15.0dev,<15.1dev',
        'odoo-addon-project_stage_mgmt>=15.0dev,<15.1dev',
        'odoo-addon-project_status>=15.0dev,<15.1dev',
        'odoo-addon-project_stock>=15.0dev,<15.1dev',
        'odoo-addon-project_stock_product_set>=15.0dev,<15.1dev',
        'odoo-addon-project_stock_request>=15.0dev,<15.1dev',
        'odoo-addon-project_task_add_very_high>=15.0dev,<15.1dev',
        'odoo-addon-project_task_code>=15.0dev,<15.1dev',
        'odoo-addon-project_task_default_stage>=15.0dev,<15.1dev',
        'odoo-addon-project_task_dependency>=15.0dev,<15.1dev',
        'odoo-addon-project_task_description_template>=15.0dev,<15.1dev',
        'odoo-addon-project_task_material>=15.0dev,<15.1dev',
        'odoo-addon-project_task_milestone>=15.0dev,<15.1dev',
        'odoo-addon-project_task_personal_stage_auto_fold>=15.0dev,<15.1dev',
        'odoo-addon-project_task_pull_request>=15.0dev,<15.1dev',
        'odoo-addon-project_task_stage_state>=15.0dev,<15.1dev',
        'odoo-addon-project_template>=15.0dev,<15.1dev',
        'odoo-addon-project_template_milestone>=15.0dev,<15.1dev',
        'odoo-addon-project_timeline>=15.0dev,<15.1dev',
        'odoo-addon-project_timeline_hr_timesheet>=15.0dev,<15.1dev',
        'odoo-addon-project_timesheet_time_control>=15.0dev,<15.1dev',
        'odoo-addon-project_type>=15.0dev,<15.1dev',
        'odoo-addon-project_wbs>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
