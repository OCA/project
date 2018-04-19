import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-project_analytic_line_view',
        'odoo8-addon-project_baseuser',
        'odoo8-addon-project_categ',
        'odoo8-addon-project_categ_issue',
        'odoo8-addon-project_classification',
        'odoo8-addon-project_closing',
        'odoo8-addon-project_description',
        'odoo8-addon-project_gtd',
        'odoo8-addon-project_issue_baseuser',
        'odoo8-addon-project_issue_code',
        'odoo8-addon-project_issue_reassign',
        'odoo8-addon-project_issue_task',
        'odoo8-addon-project_model_to_task',
        'odoo8-addon-project_recalculate',
        'odoo8-addon-project_sla',
        'odoo8-addon-project_stage_closed',
        'odoo8-addon-project_stage_state',
        'odoo8-addon-project_stage_state_issue',
        'odoo8-addon-project_task_add_very_high',
        'odoo8-addon-project_task_analytic_partner',
        'odoo8-addon-project_task_category',
        'odoo8-addon-project_task_code',
        'odoo8-addon-project_task_materials',
        'odoo8-addon-project_task_materials_analytic_partner',
        'odoo8-addon-project_task_materials_stock',
        'odoo8-addon-project_task_reassign',
        'odoo8-addon-project_timesheet_analytic_partner',
        'odoo8-addon-sale_order_project',
        'odoo8-addon-service_desk',
        'odoo8-addon-service_desk_issue',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
