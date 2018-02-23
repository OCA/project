# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import os
import urllib.parse
import hmac

from hashlib import sha1
from passlib.utils import consteq


def urljoin(base_url, *args):
    postfix = os.path.join(*args)
    return urllib.parse.urljoin(base_url, postfix)


def get_image_type(self):
    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    for record in self:
        if not record.type:
            continue
        record.image_type = "{}/project_git_{}/static/src/img/{}.png".format(
            base_url, record.type, record.type
        )


def get_avatar(self, name):
    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    for record in self:
        record.avatar = urljoin(
            base_url, 'project_git', 'static', 'src', 'img', '%s.png' % name
        )


def hmac_new(secret, message, add_sha1=False):
    digest = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        sha1
    ).hexdigest()

    if add_sha1:
        digest = 'sha1=' + digest
    return digest


def digest_compare(left, right):
    return consteq(left.encode('utf-8'), right.encode('utf-8'))
