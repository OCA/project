import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-project_list>=15.0dev,<15.1dev',
        'odoo-addon-project_parent_task_filter>=15.0dev,<15.1dev',
        'odoo-addon-project_task_add_very_high>=15.0dev,<15.1dev',
        'odoo-addon-project_task_code>=15.0dev,<15.1dev',
        'odoo-addon-project_task_default_stage>=15.0dev,<15.1dev',
        'odoo-addon-project_task_dependency>=15.0dev,<15.1dev',
        'odoo-addon-project_task_material>=15.0dev,<15.1dev',
        'odoo-addon-project_task_personal_stage_auto_fold>=15.0dev,<15.1dev',
        'odoo-addon-project_task_pull_request>=15.0dev,<15.1dev',
        'odoo-addon-project_task_stage_state>=15.0dev,<15.1dev',
        'odoo-addon-project_template>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
