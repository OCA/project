import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-project_department',
        'odoo11-addon-project_description',
        'odoo11-addon-project_key',
        'odoo11-addon-project_stage_state',
        'odoo11-addon-project_task_add_very_high',
        'odoo11-addon-project_task_code',
        'odoo11-addon-project_task_default_stage',
        'odoo11-addon-project_task_dependency',
        'odoo11-addon-project_timeline',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
