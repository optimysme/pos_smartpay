# coding: utf-8
from odoo import fields, models


class PosSession(models.Model):
    _inherit = "pos.config"

    def _has_smartpay(self):
        for r in self:
            has_smartpay = False
            for m in r.payment_method_ids:
                if m.use_payment_terminal == "smartpay":
                    has_smartpay = True
                    break
            r.has_smartpay = has_smartpay

    ################################################################################
    # Fields
    ################################################################################
    has_smartpay = fields.Boolean(readonly=True, compute="_has_smartpay")
    smartpay_register_uuid = fields.Char(string="Smartpay Pairing Code")

    ################################################################################
    # Methods
    ################################################################################
    def button_pair_smartpay(self):
        """
        :return: action to display wizard
        """
        self.ensure_one()
        wizard = self.env["pos.smartpay.pairing"].create({"pos_config": self.id})
        return {
            "type": "ir.actions.act_window",
            "name": wizard._description,
            "res_model": wizard._name,
            "res_id": wizard.id,
            "view_id": False,
            "view_mode": "form",
            "target": "new"
        }
