# Copyright 2017-19 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project Work Breakdown Structure',
    'version': '12.0.1.1.2',
    'license': 'AGPL-3',
    'author': 'Matmoz d.o.o., '
              'Luxim d.o.o., '
              'Deneroteam, '
              'Eficent, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/project',
    'depends': [
        'account_analytic_parent',
        'account_analytic_sequence',
        'hr_timesheet',
    ],
    'summary': 'Apply Work Breakdown Structure',
    'data': [
        'view/account_analytic_account_view.xml',
        'view/project_project_view.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
}
