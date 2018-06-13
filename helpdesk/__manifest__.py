# Copyright 2018 Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HelpDesk",
    "version": "11.0.1.0.0",
    "author": "Dario Lodeiros, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "website": "https://github.com/OCA/project",
    "depends": [
        "mail",
        "portal",
    ],
    "data": [
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        'data/helpdesk_data.xml',
        'views/helpdesk_ticket.xml',
        'views/helpdesk_team.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
