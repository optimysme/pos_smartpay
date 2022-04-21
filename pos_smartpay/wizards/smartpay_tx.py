# coding: utf-8

from odoo import fields, models


class SmartpayTransaction(models.TransientModel):
    """
    Smartpay POS transactions on the fly.
    """
    _name = "pos.smartpay.tx"
    _description = __doc__
    _sql_constraints = [
        ("unique_tx", "unique (transaction)", "Transaction identifiers must be unique"),
    ]

    ################################################################################
    # Fields
    ################################################################################
    pos_config = fields.Many2one("pos.config", "POS Register", readonly=True, required=True, ondelete="cascade")
    transaction = fields.Char("Transaction Id", required=True, help="As supplied by Smartpay")
    url = fields.Char("Status URL", required=True)
    state = fields.Selection([
        ("wait", "In Progress"),
        ("success", "Success"),
        ("error", "Error"),
    ], string="POS result", default="wait", required=True)
    message = fields.Char(string="POS message")
    json = fields.Text("Response", help="Latest JSON response from Smartpay")
