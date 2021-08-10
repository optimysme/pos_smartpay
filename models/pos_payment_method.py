# coding: utf-8
import logging

from odoo import models
from ..smartpay_client import SmartpayClient

_logger = logging.getLogger(__name__)

PAYMENT_TYPE = "smartpay"


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [(PAYMENT_TYPE, "Smartpay")]

    def proxy_smartpay_request(self, data, operation=False):
        """
        Invoked from Javascript front-end.

        :param data: POS state as a dictionary
        :param operation: ignorable.
        :return: True/False
        """
        _logger.debug("data={}".format(data))

        # Is this a restarted-retry?
        # - Handle case where POS is retrying a submitted payment transaction after connection failures midway
        txid = data.get("transaction", False)
        if txid:
            tx = self.env["pos.smartpay.tx"].search([("transaction", "=", txid)])
            if tx:
                _logger.info("retrying transaction={}".format(txid))
                return {
                    "submit": True,
                    "error": "",
                    "transaction": tx.transaction,
                }
            else:
                _logger.info("retry not found, transaction={} -> resubmitting".format(txid))

        # Initiate a transaction-request to SmartPay
        pos_config = self.env["pos.config"].browse(data["pos"])
        client = SmartpayClient(pos_config)
        if data["amount"] > 0:
            success, result = client.purchase(data["amount"], False)
        else:
            success, result = client.refund(data["amount"], False)
        if success:
            return {
                "submit": True,
                "error": "",
                "transaction": result.transaction,
            }
        return {
            "submit": False,
            "error": result,
            "transaction": "",
        }

    def get_smartpay_status(self, txid):
        """
        Polling endpoint, invoked from Javascript front-end to query transaction status.

        :param pos_config_id:
        :return:
        """
        self.ensure_one()

        tx = self.env["pos.smartpay.tx"].search([("transaction", "=", txid)])
        if not tx:
            _logger.error("transaction={} not found".format(txid))
            return {
                "state": "error",
                "message": "Transaction not found",
            }
        if tx.state == "wait":
            SmartpayClient(tx.pos_config).transaction_status(tx)

        return {
            "state": tx.state,
            "message": tx.message,
        }
