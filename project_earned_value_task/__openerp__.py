# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Earned Value Task",
    "summary": "Manage the progress of your projects using the Earned Value "
               "Management technique.",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services SL,"
              "Odoo Community Association (OCA)",
    "website": "www.eficent.com",
    "category": "Generic Modules/Projects & Services",
    "depends": ["project", "hr_timesheet"],
    "init_xml": [],
    "data": [
        "views/project_evm_view.xml",
        "views/project_view.xml",
        "wizards/earned_value_view.xml",
        "data/project_data.xml",
    ],
    'demo': [

    ],
    'installable': True,
}
