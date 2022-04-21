odoo.define(
    "pos_smartpay.models",
    function (require)
    {
        var models = require("point_of_sale.models");
        var PaymentSmartPay = require("pos_smartpay.payment");
        models.register_payment_method("smartpay", PaymentSmartPay);
    });
