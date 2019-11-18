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
        'odoo13-addon-project_parent_task_filter',
        'odoo13-addon-project_stage_closed',
        'odoo13-addon-project_task_add_very_high',
        'odoo13-addon-project_task_code',
        'odoo13-addon-project_task_default_stage',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
