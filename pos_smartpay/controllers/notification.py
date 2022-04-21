# coding: utf-8
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

NOTIFICATION_ROUTE = "/pos_smartpay/notification"


class SmartpayNotification(http.Controller):
    @http.route(NOTIFICATION_ROUTE, type="json", methods=["POST"], auth="none", csrf=False)
    def notification(self):
        """
        TODO: Non-working code
        """
        data = json.loads(request.httprequest.data)
        _logger.error("please get this working")
