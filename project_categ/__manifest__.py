# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project Configurable Categories',
    'summary': 'Allow for Project specific category lists for Tasks',
    'version': '10.0.0.1.0',
    "category": "Project Management",
    'description': """\
To setup:

  1. Create a parent Category (Tag). E.g. "System Type".
  2. Create categories to be made available as child.
     E.g. "Computer", "Printer", ...
  3. On the Project form, Other Info tab, set the "Root Category".

Now make this feature available on Issues or Tasks by installing the
corresponding extension module.
""",
    'author': "Daniel Reis, Tecnativa, Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'license': 'AGPL-3',
    'depends': [
        'project',
        ],
    'data': [
        'views/project_categ_view.xml',
        ],
    'installable': True,
    'application': False,
}
