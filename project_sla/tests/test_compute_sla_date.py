from openerp.tests.common import TransactionCase
import datetime

dt_combine = datetime.datetime.combine
dt_delta = datetime.timedelta

thursday = datetime.date(2015, 4, 9)
friday = thursday + dt_delta(days=1)
monday = friday + dt_delta(days=3)

thursday_8 = dt_combine(thursday, datetime.time(8))
thursday_10 = dt_combine(thursday, datetime.time(10))
thursday_15 = dt_combine(thursday, datetime.time(15))
thursday_17 = dt_combine(thursday, datetime.time(17))
thursday_19 = dt_combine(thursday, datetime.time(19))

friday_5 = dt_combine(friday, datetime.time(5))
friday_9 = dt_combine(friday, datetime.time(9))
friday_11 = dt_combine(friday, datetime.time(11))

monday_10 = dt_combine(monday, datetime.time(10))


class TestComputeSlaDate(TransactionCase):
    """ Test _compute_sla_date
    """

    def setUp(self):
        super(TestComputeSlaDate, self).setUp()

        self.model = self.registry['project.sla.control']
        # Tests using 8-12 13-18 demo data calendar
        self.calendar_id = self.ref('resource.timesheet_group1')

    def test_10(self):
        cr, uid = self.cr, self.uid
        model = self.model
        calendar_id = self.calendar_id

        def compute(date, hours, context=None):
            # Calculation depend on timezone
            # Use UTC if none is specified
            if context is None:
                context = {'tz': 'UTC'}
            return model._compute_sla_date(
                cr, uid, calendar_id, uid, date, hours, context=context)

        self.assertEquals(compute(thursday_8, 2), thursday_10)

        # 1 hour time for a lunch break
        self.assertEquals(compute(thursday_10, 4), thursday_15)

        # working day ands in 18, so 17 + 2 hours must be friday 9
        self.assertEquals(compute(thursday_17, 2), friday_9)

        # when start_date is after end of working day
        # 3 hours count from 08:00 to 11:00
        self.assertEquals(compute(thursday_19, 3), friday_11)

        # when start_Date is before start of working day
        self.assertEquals(compute(friday_5, 3), friday_11)

        # end date should be moved correctly on next day
        self.assertEquals(compute(thursday_10, 10), friday_11)

        # correctly process weekends
        self.assertEquals(compute(thursday_15, 3 + 9 + 2), monday_10)

    # TODO: test it with leaves
