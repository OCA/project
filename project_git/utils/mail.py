# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.tools.mail import _Cleaner

_Cleaner._style_whitelist.append("vertical-align")
_Cleaner._style_whitelist.append("display")
_Cleaner._style_whitelist.append("text-decoration")
