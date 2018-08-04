# Copyright 2013 Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Order Project',
    'version': '11.0.1.0.0',
    'category': 'Project',
    'summary': 'Create a Project from Sale Order',
    'license': 'AGPL-3',
    'author': 'Akretion, AvanzOSC, Serv. Tecnol. Avanzados - Pedro M. Baeza, Adaptive City - Aitor Bouzas, José Luis Sandoval Alaguna, Odoo Community Association (OCA)',
    'complexity': 'easy',
    'description': """
Sale Order Project
==================
Link module to map sale orders to project
        """,
    'website': 'http://www.akretion.com/',
    'depends': [
        'project',
        'sale',
    ],
    'data': [
        'views/sale_view.xml',
    ],
    'installable': True,
}
