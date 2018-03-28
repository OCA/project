# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import logging
import time
from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class AnalyticAccountSequence(models.Model):
    _name = 'analytic.account.sequence'

    @api.depends('number_next', 'implementation')
    def _compute_number_next_actual(self):
        """Return number from ir_sequence row when no_gap implementation,
        and number from postgres sequence when standard implementation."""
        if not self.ids:
            return True
        for element in self:
            if element.implementation != 'standard':
                element.number_next_actual = element.number_next
            else:
                # get number from postgres sequence. Cannot use
                # currval, because that might give an error when
                # not having used nextval before.
                statement = (
                    "SELECT last_value, increment_by, is_called"
                    " FROM analytic_account_sequence_%05d"
                    % element.id)
                self._cr.execute(statement)
                (last_value, increment_by, is_called) = self._cr.fetchone()
                if is_called:
                    element.number_next_actual = last_value + increment_by
                else:
                    element.number_next_actual = last_value

    @api.model
    def _code_get(self):
        self._cr.execute('select code, name from ir_sequence_type')
        return self._cr.fetchall()

    @api.model
    def _inverse_number_next_actual(self):
        return self.write({'number_next': self.number_next or 0})

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic account',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        'Name',
        required=True
    )
    code = fields.Selection(
        string='Code',
        selection='_code_get',
        default=False
    )
    implementation = fields.Selection(
        [('standard', 'Standard'), ('no_gap', 'No gap')],
        'Implementation',
        required=True,
        default="standard",
        help="Two sequence object "
        "implementations are offered: Standard "
        "and 'No gap'. The later is slower than "
        "the former but forbids any gap in the"
        " sequence (while they are possible"
        " in the former)."
    )
    active = fields.Boolean(
        'Active',
        default=True
    )
    prefix = fields.Char(
        'Prefix',
        help="Prefix value of the record for "
        "the sequence"
    )
    suffix = fields.Char(
        'Suffix',
        help="Suffix value of the record for "
        "the sequence"
    )
    number_next = fields.Integer(
        'Next Number',
        required=True,
        default=1,
        help="Next number of this sequence"
    )
    number_next_actual = fields.Integer(
        compute='_compute_number_next_actual',
        inverse='_inverse_number_next_actual',
        required=True, string='Next Number',
        default=1, store=True,
        help='Next number that will be used. '
        'This number can be incremented '
        'frequently so the displayed value '
        ' might already be obsolete'
    )
    number_increment = fields.Integer(
        'Increment Number',
        required=True,
        default=1,
        help="The next number of the "
        "sequence will be incremented "
        "by this number"
    )
    padding = fields.Integer(
        'Number Padding',
        required=True,
        default=0,
        help="OpenERP will automatically adds some '0' on"
        " the left of the 'Next Number' to get the "
        "required padding size."
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self:
            self.env['res.company']._company_default_get(
                'analytic.account.sequence'
            )
    )

    _sql_constraints = [
        (
            'unique_analytic_account_id',
            'unique (analytic_account_id)',
            'The analytic account must be unique'
        )
    ]

    @api.multi
    def _create_sequence(self, number_increment, number_next):
        """ Create a PostreSQL sequence.
        There is no access rights check.
        """
        self.ensure_one()
        if number_increment == 0:
            raise UserError(_("Increment number must not be zero."))
        assert isinstance(self.id, (int, long))
        sql = (
            "CREATE SEQUENCE analytic_account_sequence_%05d "
            "INCREMENT BY %%s START WITH %%s" % self.id
        )
        self._cr.execute(sql, (number_increment, number_next))

    @api.multi
    def _drop_sequence(self):
        """ Drop the PostreSQL sequence if it exists.
        There is no access rights check.
        """
        ids = self.ids if isinstance(self.ids, list) else list(self.ids)
        assert all(
            isinstance(
                i, (int, long)
            ) for i in ids
        ), "Only ids in (int, long) allowed."
        names = ','.join('analytic_account_sequence_%05d' % i for i in ids)
        # RESTRICT is the default; it prevents dropping the sequence if an
        # object depends on it.
        self._cr.execute("DROP SEQUENCE IF EXISTS %s RESTRICT " % names)

    @api.multi
    def _alter_sequence(self, number_increment, number_next=None):
        """ Alter a PostreSQL sequence.
        There is no access rights check.
        """
        if number_increment == 0:
            raise UserError(_("Increment number must not be zero."))
        assert isinstance(self.id, (int, long))
        seq_name = 'analytic_account_sequence_%05d' % (self.id,)
        self._cr.execute("SELECT relname FROM pg_class WHERE relkind = %s "
                         "AND relname=%s", ('S', seq_name))
        if not self._cr.fetchone():
            # sequence is not created yet, we're inside create() so
            # ignore it, will be set later
            return
        statement = "ALTER SEQUENCE %s INCREMENT BY %d" % (seq_name,
                                                           number_increment)
        if number_next is not None:
            statement += " RESTART WITH %d" % (number_next, )
        self._cr.execute(statement)

    @api.model
    def create(self, values):
        """ Create a sequence, in implementation == standard a
        fast gaps-allowed PostgreSQL sequence is used.
        """
        values = self._add_missing_default_values(values)
        values = super(AnalyticAccountSequence, self).create(values)
        if values.implementation == 'standard':
            values._create_sequence(values.number_increment,
                                    values.number_next)
        return values

    @api.multi
    def unlink(self):
        super(AnalyticAccountSequence, self).unlink()
        self._drop_sequence()
        return True

    @api.multi
    def write(self, values):
        new_implementation = values.get('implementation')
        super(AnalyticAccountSequence, self).write(values)
        for row in self:
            # 4 cases: we test the previous impl. against the new one.
            i = values.get('number_increment', row.number_increment)
            n = values.get('number_next', row.number_next)
            if row.implementation == 'standard':
                if new_implementation in ('standard', None):
                    # Implementation has NOT changed.
                    # Only change sequence if really requested.
                    if values.get('number_next'):
                        row._alter_sequence(i, n)
                    else:
                        # Just in case only increment changed
                        row._alter_sequence(i)
                else:
                    row._drop_sequence()
            else:
                if new_implementation in ('no_gap', None):
                    pass
                else:
                    row._create_sequence(i, n)
        return True

    @api.model
    def _interpolate(self, s, d):
        if s:
            return s % d
        return ''

    @api.model
    def _interpolation_dict(self):
        # Actually, the server is always in UTC.
        t = time.localtime()
        return {
            'year': time.strftime('%Y', t),
            'month': time.strftime('%m', t),
            'day': time.strftime('%d', t),
            'y': time.strftime('%y', t),
            'doy': time.strftime('%j', t),
            'woy': time.strftime('%W', t),
            'weekday': time.strftime('%w', t),
            'h24': time.strftime('%H', t),
            'h12': time.strftime('%I', t),
            'min': time.strftime('%M', t),
            'sec': time.strftime('%S', t),
        }

    @api.multi
    def _next(self):
        if not self._ids:
            return False
        force_company = self._context.get('force_company')
        if not force_company:
            force_company = self.env['res.users'].\
                browse(self._uid).company_id.id
        preferred_sequences = [s for s in self if s.company_id and
                               s.company_id[0] == force_company]
        seq = preferred_sequences[0] if preferred_sequences else self[0]
        if seq.implementation == 'standard':
            self._cr.execute(
                "SELECT nextval('analytic_account_sequence_%05d')" % seq.id)
            seq.number_next = self._cr.fetchone()
        else:
            self._cr.execute("SELECT number_next FROM "
                             "analytic_account_sequence WHERE id=%s"
                             "FOR UPDATE NOWAIT", (seq.id,))
            self._cr.execute(
                "UPDATE analytic_account_sequence "
                "SET number_next=number_next+number_increment "
                "WHERE id=%s ", (seq.id,))
        d = self._interpolation_dict()
        try:
            interpolated_prefix = self._interpolate(seq.prefix, d)
            interpolated_suffix = self._interpolate(seq.suffix, d)
        except ValueError:
            raise UserError(
                _(
                    'Invalid prefix or suffix for sequence \'%s\''
                ) %
                (seq.get('name'))
            )
        return interpolated_prefix + '%%0%sd' % seq[
            'padding'] % seq['number_next'] + interpolated_suffix

    @api.model
    def next_by_id(self, sequence_id):
        """ Draw an interpolated string using the specified sequence."""
        self.check_access_rights('read')
        company_ids = self.env['res.company'].search([])
        ids = self.search(['&', ('id', '=', sequence_id),
                           ('company_id', 'in', company_ids.ids)])
        return ids._next()

    @api.model
    def next_by_code(self, sequence_code):
        """
        Draw an interpolated string using a sequence with the requested code.
       If several sequences with the correct code are available to the user
       (multi-company cases), the one from the user's current company will
       be used.
       :param dict context: context dictionary may contain a
       ``force_company`` key with the ID of the company to
       use instead of the user's current company for the
       sequence selection. A matching sequence for that
       specific company will get higher priority.
       """
        self.check_access_rights('read')
        company_ids = self.env['res.company'].search([]) + [False]
        ids = self.search(['&', ('code', '=', sequence_code),
                           ('company_id', 'in', company_ids)])
        return ids._next()

    @api.model
    def get_id(self, sequence_code_or_id, code_or_id='id'):
        """ Draw an interpolated string using the specified sequence.

        The sequence to use is specified by the ``sequence_code_or_id``
        argument, which can be a code or an id (as controlled by the
        ``code_or_id`` argument. This method is deprecated.
        """
        # TODO: bump up to warning after 6.1 release
        _logger.debug("ir_sequence.get() and ir_sequence.get_id() "
                      "are deprecated. Please use ir_sequence.next_by_code() "
                      "or ir_sequence.next_by_id().")
        if code_or_id == 'id':
            return self.next_by_id(sequence_code_or_id)
        else:
            return self.next_by_code(sequence_code_or_id)

    @api.model
    def get(self, code):
        """ Draw an interpolated string using the specified sequence.
        The sequence to use is specified by its code. This method is
        deprecated.
        """
        return self.get_id(code, 'code')
