# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


{
    'name': "Project Security Group",
    'category': 'Project Management',
    'summary': 'Add Project roles to more flexibility teams',
    'version': '8.0.1.0.0',
    'depends': ['project_stage_state'],
    'data': [
        'security/project_security_group_security.xml',
        'views/project_security_group_menu.xml',
        'views/res_config_view.xml',
        'security/ir.model.access.csv',
    ],
    'author': 'Antiun Ingeniería S.L.,'
              'Incaser Informatica S.L.,  '
              'Odoo Community Association (OCA)',
    'website': 'http://www.incaser.es',
    'license': 'AGPL-3',
    'installable': True,
}
