# Smartpay POS Integration

This module integrates [Smartpay](https://smartpay.co.nz) POS terminals with
Odoo's POS module.

Endpoints are configured into the rc files::

    [pos_smartpay]
	endpoint = https://api.smart-connect.cloud/POS
		
Possible *endpoint* values are available here: 
https://smartpaydev.com/reference/sending-api-requests.html


* https://api-dev.smart-connect.cloud/POS (development)
* https://api.smart-connect.cloud/POS (production)
