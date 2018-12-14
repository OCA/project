# -*- coding: utf-8 -*-
{
    'name': 'Link Sale Order to Project',
    'summary': 'Create project / tasks from Sale Order',
    'version': '10.0.1.0.0',
    "author": "Le Filament, Odoo Community Association (OCA)",
    'maintainers': ["remi-filament"],
    'license': 'AGPL-3',
    'depends': ['sale_timesheet', 'project'],
    'data': [
        'views/product_views.xml',
        'views/sale_config_settings_views.xml',
        'wizard/sale_views_wizard.xml',
        'views/sale_views.xml',
        'views/project_config_views.xml',
        'views/project_views.xml',
        'views/project_task_views.xml',
    ],
}
