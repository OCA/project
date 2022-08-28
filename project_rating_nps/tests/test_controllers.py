# Copyright 2020-today Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import html

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from odoo.service import wsgi_server
from odoo.tests.common import HttpCase

from .common import RatingTestMixin


class TestControllers(RatingTestMixin, HttpCase):

    def test_open_rating(self):
        " Check rating_apply override works and uses present module images "

        test_client = Client(wsgi_server.application, BaseResponse)
        werkzeug_environ = {"REMOTE_ADDR": "127.0.0.1"}

        response = test_client.get("/rating/%s/7" % self.rating.access_token,
                                   environ_base=werkzeug_environ)

        self.assertIn("7/10", response.data.decode("utf-8"))

        doc = html.fromstring(response.data)
        self.assertEqual(doc.xpath('//img/@src'),
                         ["/project_rating_nps/static/src/img/passive.png"])
