# -*- coding: utf-8 -*-
# (c) 2013 Daniel Reis
# (c) 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Per Project Configurable Categorie on Issues',
    'summary': 'Projects Issues can have an allowed category list',
    'version': '0.1.0',
    "category": "Project Management",
    'description': """\
Adds to Issues the ability to limit selectable Categories to a Project's
specific list.
""",
    'author': "Daniel Reis, Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
        'project_categ',
        ],
    'data': [
        'views/project_categ_view.xml',
        ],
    'installable': True,
    'auto_install': True,
}
