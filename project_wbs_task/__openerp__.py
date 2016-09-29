# -*- coding: utf-8 -*-

{
<<<<<<< ff33f76c66d1cedc6dbd60cdf85ad0855da08321
    "name": "Work Breakdown Structure - Tasks",
    "version": "2.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Generic Modules/Projects & Services",
    "depends": ["project_wbs"],
    "description": """
Work Breakdown Structure - Tasks
================================
This module extends the standard Odoo functionality by adding:

- A button in the project tree view that will conduct the user to the list
view for the associated tasks.
- The possibility to search for task by the WBS complete reference or name.

    """,
    "data": [
        "view/project_task_view.xml",
        "view/project_view.xml",
=======
    'name': 'Work Breakdown Structure - Tasks',
    'version': '8.0.2.0.2',
    'author':   'Eficent, '
                'Serpent CS, '
                'Matmoz d.o.o., '
                'Project Expert Team',
    'contributors': [
        'Jordi Ballester <jordi.ballester@eficent.com>',
        'Matjaž Mozetič <m.mozetic@matmoz.si>',
        'Sudhir Arya <>'
    ],
    'website': 'http://project.expert',
    'category': 'Project Management',
    'license': 'AGPL-3',
    'depends': ['project_wbs'],
    'data': [
        'view/project_task_view.xml',
        'view/project_view.xml',
>>>>>>> Enhance the module descriptions
    ],
    'demo': [

    ],
    'test': [
    ],
    'installable': True,
    'application': True,
}
