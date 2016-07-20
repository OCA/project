# -*- coding: utf-8 -*-
{
    'name': 'Project Task Delegate',
    'version': '1.0',
    'category': 'Projects & Services',
    'sequence': 10,
    'summary': '',
    'description': """
Project Task Delegate
=====================
    """,
    'author': 'Karsten Kinateder',
    'website': 'www.plustron.de',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'project_timesheet',
        'project_task_default_stage',  # https://github.com/OCA/project/tree/9.0/project_task_default_stage
    ],
    'data': [
        'security/project_task_security.xml',
        'views/project_task_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
