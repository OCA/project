import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-project_department>=16.0dev,<16.1dev',
        'odoo-addon-project_list>=16.0dev,<16.1dev',
        'odoo-addon-project_role>=16.0dev,<16.1dev',
        'odoo-addon-project_stock>=16.0dev,<16.1dev',
        'odoo-addon-project_task_add_very_high>=16.0dev,<16.1dev',
        'odoo-addon-project_task_default_stage>=16.0dev,<16.1dev',
        'odoo-addon-project_task_personal_stage_auto_fold>=16.0dev,<16.1dev',
        'odoo-addon-project_template>=16.0dev,<16.1dev',
        'odoo-addon-project_timeline>=16.0dev,<16.1dev',
        'odoo-addon-project_type>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
