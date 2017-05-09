# -*- coding: utf-8 -*-
# © 2010-2013 Akretion LDTA (<http://www.akretion.com>)
# © 2013 Akretion (http://www.akretion.com).
# © Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Order Project',
    'version': '8.0.1.1.0',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'author': 'Akretion, '
              'AvanzOSC, '
              'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Didotech srl, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com/',
    'depends': [
        'project',
        'sale',
    ],
    'data': [
        'views/sale_view.xml',
        'views/project_view.xml',
        'wizard/order_select_view.xml'
    ],
    'installable': True,
}
