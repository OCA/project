# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Webhook for Gitlab',
    'summary': 'Controllers needed to notify actions with gitlab',
    'version': '12.0.1.0.0',
    'category': 'Development',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'helpdesk',
        'project',
    ],
    'data': [
        'views/message_templates.xml',
        'data/ir_config_parameter.xml',
    ],
    'external_dependencies': {
        'python': [
            'gitlab',
        ],
    },
}
