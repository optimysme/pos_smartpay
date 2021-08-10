# coding: utf-8
import uuid

from odoo import fields, models
from ..smartpay_client import SmartpayClient


class SmartpayPairing(models.TransientModel):
    """
    Smartpay POS pairing
    """
    _name = "pos.smartpay.pairing"
    _description = __doc__

    ################################################################################
    # Fields
    ################################################################################
    pos_config = fields.Many2one("pos.config", "POS Register", readonly=True, required=True, ondelete="cascade")
    paircode = fields.Char("Paircode")
    error = fields.Text("Pairing Error", readonly=True)

    def button_attempt_pair(self):
        """
        Initiate Pairing Conversation.

        https://www.smartpaydev.com/reference/pairing-endpoint.html#pairing-flow

        :return: close or the current self with failure message
        """

        # When pairing, always regenerate a new UUID, just to be safe security-wise
        self.pos_config.write({"smartpay_register_uuid": str(uuid.uuid4())})

        client = SmartpayClient(self.pos_config)
        success, message = client.pair(self.paircode)
        if success:
            return {"type": "ir.actions.act_window_close"}

        self.pos_config.write({"smartpay_register_uuid": False})  # clear out
        self.write({"error": message})
        return {
            "type": "ir.actions.act_window",
            "name": self._description,
            "res_model": self._name,
            "res_id": self.id,
            "view_id": False,
            "view_mode": "form",
            "target": "new"
        }
