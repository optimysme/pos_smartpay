# coding: utf-8
import logging

import requests

from odoo.tools.config import config
from odoo.tools.float_utils import float_round
from .controllers.notification import NOTIFICATION_ROUTE

#
# The Smartpay API endpoint is specified in the rc file
# ie:
# [pos_smartpay]
#
# endpoint = https://....
#
SECTION_NAME = "pos_smartpay"
API_ENDPOINT = config.get_misc(SECTION_NAME, "endpoint")

_logger = logging.getLogger(__name__)


class SmartpayClient():
    """
    Simple endpoint wrapper.

    Note that the pos_register_id is scoped with the database-name,
    as the data may move between production and uat, and we don't
    want a POS on UAT to register transactions against Production.
    """

    def __init__(self, pos_config):
        """
        :param pos_config: pos.config record
        """
        self.env = pos_config.env
        self.pos = pos_config
        self.pos_register_id = "{}/{}".format(self.env.cr.dbname, pos_config.smartpay_register_uuid)
        self.user = self.env.user.partner_id.name

        modulename = __name__.split(".")[2]  # odoo.addons.{modulename}.etc.etc
        module = self.env["ir.module.module"].search([("name", "=", modulename)])
        self.vendor = module.author

    def _populate_base(self, data):
        data.update(
            {
                "POSRegisterID": self.pos_register_id,
                "POSBusinessName": self.pos.company_id.name,
                "POSVendorName": self.vendor,
            })
        return data

    def pair(self, paircode):
        """
        Attempt pairing.

        https://www.smartpaydev.com/reference/pairing-endpoint.html

        :param paircode:
        :param pos_config: pos.config record
        :return: (True/False, "error message")
        """
        url = "{}/Pairing/{}".format(API_ENDPOINT, paircode)
        try:
            data = self._populate_base(
                {
                    "POSRegisterName": self.pos.name,
                    "Contact Name": self.user,
                })
            _logger.debug("put={}".format(url))
            response = requests.put(url, data=data)
            if response.status_code == 200:
                _logger.debug("paired pos.config={}".format(self.pos.name))
                result = (True, "success")
            elif response.status_code == 400:
                data = response.json()
                result = (False, data["error"])
            else:
                result = (False, "status={}".format(response.status_code))

        except Exception as e:
            _logger.error("pairing failed url={}".format(url), exc_info=e)
            result = (False, "exception={}".format(e))

        return result

    def _async_smartpay(self, tx_type, amount, enable_callback):
        """
        Send an async purchase request.

        https://www.smartpaydev.com/reference/transaction-types.html#card-purchase

        :param amount:
        :param enable_callback: enable/disable callback (intended for development purposes)
        :return: (True, pos.smartpay.tx) or (False, error-message)
        """
        data = self._populate_base(
            {
                "TransactionMode": "ASYNC",
                "TransactionType": tx_type,
                "AmountTotal": int(float_round(amount * 100, precision_digits=0)),  # in cents
            })
        if enable_callback:
            website = self.env["website"].get_current_website()
            callback = "{}/{}".format(website.get_base_url(), NOTIFICATION_ROUTE)
            data["PosNotificationCallbackUrl"] = callback,

        url = "{}/Transaction".format(API_ENDPOINT)
        try:
            _logger.debug("post={}".format(url))
            response = requests.post(url, data=data)  # application/x-www-form-urlencoded

            if response.status_code != 200:
                _logger.error("response-code={}".format(response.status_code))
                return (False, "Smartpay Remote failure")

            # Extract essential details from the response
            # https://www.smartpaydev.com/reference/transaction-endpoint.html#api-response
            body = response.json()
            body_data = body["data"]
            _logger.debug("response={}".format(body))
            tx = self.env["pos.smartpay.tx"].create(
                {
                    "pos_config": self.pos.id,
                    "transaction": body["transactionId"],
                    "url": body_data["PollingUrl"],
                    "json": body,
                })
            return (True, tx)

        except Exception as e:
            _logger.error("purchase failed url={}".format(url), exc_info=e)
            return (False, "exception={}".format(e))

    def purchase(self, amount, enable_callback=True):
        return self._async_smartpay("Card.Purchase", amount, enable_callback)

    def refund(self, amount, enable_callback=True):
        return self._async_smartpay("Card.Refund", abs(amount), enable_callback)

    def transaction_status(self, tx):
        """
        Query Smartpay for state for transaction.

        :param tx: pos.smartpay.tx record
        """
        result = message = body = "?"
        try:
            # Poll the status URL as given
            _logger.debug("get={}".format(tx.url))
            response = requests.get(tx.url)

            if response.status_code == 404:
                result = "error"
                message = "invalid url {}".format(tx.url)

            else:
                body = response.json()
                # https://www.smartpaydev.com/reference/transaction-endpoint.html#api-response-http-status-codes
                if response.status_code in (400, 429):
                    result = "error"
                    message = body["error"]
                else:
                    # https://www.smartpaydev.com/reference/transaction-endpoint.html#polling-for-the-outcome
                    body_data = body["data"]

                    if body["transactionStatus"] == "PENDING":
                        result = "wait"
                    else:
                        # status = COMPLETED : okay or bad?
                        tx_status = body_data["TransactionResult"]
                        if tx_status == "OK-ACCEPTED":
                            result = "success"
                            message = "Completed"
                        elif tx_status == "OK-DECLINED":
                            result = "error"
                            message = "Declined"
                        elif tx_status == "OK-UNAVAILABLE":
                            result = "error"
                            message = "Service unavailable at this time"
                        elif tx_status == "CANCELLED":
                            result = "error"
                            message = "Transaction Cancelled"
                        else:
                            result = "error"
                            message = "Smartpay service failure"
                        _logger.debug("done result={}, message={}".format(result, message))

        except Exception as e:
            result = "error"
            message = "exception={}".format(e)

        # Always update transaction with latest result
        tx.write(
            {
                "state": result,
                "message": message,
                "json": body,
            })
