# -*- coding: utf-8 -*-
# © 2012 - 2013 Daniel Reis
# © 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# © 2017 - Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project Task Materials',
    'summary': 'Record products spent in a Task',
    'version': '1.0.0',
    'category': "Project Management",
    'author': "Tecnativa, Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'license': 'AGPL-3',
    'description': """\
Project Tasks allow to record time spent, but some activities, such as
Field Service, often require you to keep a record of the materials spent.

This module adds the ability to also this material spending.
To use it, make sure the "Log work activities on tasks" Project setting is
activated.

Note that only a simple record is made and no accounting or stock moves are
actually performed.""",
    'depends': ['project', 'product'],
    'data': [
        'views/project_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
