# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa
# © 2016 Pedro M. Baeza
# © 2016 Sergio Teruel
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project timesheet time control',
    'version': '10.0.1.0.0',
    'category': 'Project',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Antiun Ingeniería S.L.',
    'website': 'https://www.tecnativa.com',
    'depends': ['hr_timesheet'],
    'data': [
        'security/project_security.xml',
        'views/account_analytic_line_view.xml',
        'views/project_task_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
