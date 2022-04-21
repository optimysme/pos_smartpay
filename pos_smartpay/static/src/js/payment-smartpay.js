odoo.define(
    "pos_smartpay.payment",
    function (require)
    {
        "use strict";

        var core = require("web.core");
        var rpc = require("web.rpc");
        var PaymentInterface = require("point_of_sale.PaymentInterface");
        const { Gui } = require("point_of_sale.Gui");

        var _t = core._t;

        var PaymentSmartpay = PaymentInterface.extend({

            /*
             * Override external interfaces.
             */
            send_payment_request:
                function (cid)
                {
                    this._super.apply(this, arguments);
                    this._reset_state();
                    return this._smartpay_pay();
                },
            send_payment_cancel:
                function (order, cid)
                {
                    this._super.apply(this, arguments);
                    // set only if we are polling
                    this.was_cancelled = !!this.polling;
                    this._smartpay_cancel();
                    return new Promise(
                        function (resolve, reject)
                        {
                            resolve(true);
                            return Promise.resolve();
                        });
                },
            close:
                function ()
                {
                    this._super.apply(this, arguments);
                },

            /*
             * Internal Methods
             */
            _reset_state:
                function ()
                {
                    this.was_cancelled = false;
                    this.last_diagnosis_service_id = false;
                    this.remaining_polls = 15;
                    clearTimeout(this.polling);
                },

            _handle_odoo_connection_failure:
                function (data)
                {
                    // handle timeout
                    var line = this.pos.get_order().selected_paymentline;
                    if (line)
                        line.set_payment_status('retry');
                    this._show_error(_('Could not connect to the Odoo server, please check your internet connection and try again.'));

                    return Promise.reject(data); // prevent subsequent onFullFilled's from being called
                },

            _call_smartpay:
                function (data, operation)
                {
                    return rpc.query(
                        {
                            model: "pos.payment.method",
                            method: "proxy_smartpay_request",
                            args: [[this.payment_method.id], data, operation],
                        },
                        {
                            // When a payment terminal is disconnected it takes
                            // a while to return an error (~6s). So wait 10 seconds
                            // before concluding Odoo is unreachable.
                            timeout: 10000,
                            shadow: true,
                        }).catch(this._handle_odoo_connection_failure.bind(this));
                },

            _smartpay_pay:
                function ()
                {
                    var self = this;

                    var config = this.pos.config;
                    var order = this.pos.get_order();
                    var line = order.selected_paymentline;
                    var data = {
                        "pos": config.id,
                        "order": order.id,
                        "transaction": line.transaction_id,
                        "amount": line.get_amount(),
                    };

                    return this
                        ._call_smartpay(data)
                        .then(
                            function (data)
                            {
                                return self._smartpay_pay_response(data);
                            });
                },

            _smartpay_cancel:
                function ()
                {
                    /*
                     * This is just stub code, as Smartpay doesn't have API support
                     * for the POS to abort the transaction.
                     */
                },

            _poll_pay_response:
                function (resolve, reject, txid)
                {
                    var self = this;
                    if (this.was_cancelled) {
                        resolve(false);
                        return Promise.resolve();
                    }

                    return rpc.query(
                        {
                            model: 'pos.payment.method',
                            method: 'get_smartpay_status',
                            args: [[this.payment_method.id], txid],
                        },
                        {
                            timeout: 5000,
                            shadow: true,
                        })
                        .catch(
                            function (data)
                            {
                                reject();
                                return self._handle_odoo_connection_failure(data);
                            })
                        .then(
                            function (response)
                            {
                                self.remaining_polls--;

                                var order = self.pos.get_order();
                                var line = order.selected_paymentline;
                                var state = response.state;

                                if (state == "success")
                                {
                                    resolve(true);

                                } else if (state == "error")
                                {
                                    self._show_error(_.str.sprintf(_t("Message from Smartpay: %s"), response.message));

                                    line.set_payment_status("retry");
                                    reject();

                                } else if (self.remaining_polls <= 0)
                                {
                                    self._show_error(_t('The connection to your payment terminal failed. Please check if it is still connected to the internet.'));
                                    self._smartpay_cancel();
                                    resolve(false);
                                }
                            });
                },

            _smartpay_pay_response:
                function (response)
                {
                    var order = this.pos.get_order();
                    var line = order.selected_paymentline;

                    if (!response.submit)
                    {
                        this._show_error(_t(response.error));
                        if (line)
                            line.set_payment_status('force_done');
                        return Promise.resolve();
                    }

                    line.transaction_id = response.transaction;     // record for cancel/re-try
                    line.set_payment_status('waitingCard');         // this saves to local-store

                    var self = this;
                    var res = new Promise(
                        function (resolve, reject)
                        {
                            // clear previous intervals just in case, otherwise it'll run forever
                            clearTimeout(self.polling);

                            self.polling = setInterval(
                                function ()
                                {
                                    self._poll_pay_response(resolve, reject, response.transaction);
                                }, 4000);
                        });

                    // make sure to stop polling when we're done
                    res.finally (
                        function ()
                        {
                            self._reset_state();
                        });

                    return res;
                },

            _show_error:
                function (msg, title)
                {
                    if (!title)
                        title =  _t("Smartpay Error");
                    Gui.showPopup("ErrorPopup",
                        {
                            "title": title,
                            "body": msg,
                        });
                },
        });

        return PaymentSmartpay;
    });
