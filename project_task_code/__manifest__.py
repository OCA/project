# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sequential Code for Tasks",
    "version": "10.0.1.0.0",
    "category": "Project Management",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "http://www.avanzosc.es",
    "license": "AGPL-3",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristo@gmail.com>",
        "Vicent Cubells <vicent.cubells@tecnativa.com>",
    ],
    "depends": [
        "project",
    ],
    "data": [
        "data/task_sequence.xml",
        "views/project_view.xml",
    ],
    'installable': True,
    "pre_init_hook": "create_code_equal_to_id",
    "post_init_hook": "assign_old_sequences",
}
