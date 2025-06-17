# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class SomethingCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        # TODO Replace this for something useful or delete this method
        self.do_something_before_all_tests()

    def tearDown(self, *args, **kwargs):
        # TODO Replace this for something useful or delete this method
        self.do_something_after_all_tests()

        return super().tearDown(*args, **kwargs)

    def test_something(self):
        """First line of docstring appears in test logs.

        Other lines do not.

        Any method starting with ``test_`` will be tested.
        """
        pass
