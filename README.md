# Smartpay POS Integration

This module integrates [Smartpay](https://smartpay.co.nz) POS terminals with Odoo's [POS module](https://www.odoo.com/app/point-of-sale-shop).  
## In scope:
- Pairing with the eftpos terminal
- Purchase handling
- Refund Handling
All other operations such as QR codes, tipping etc are not supported.

Endpoints are configured in the rc files:

    [pos_smartpay]
	endpoint = https://api.smart-connect.cloud/POS
		
Possible *endpoint* values are available here: https://smartpaydev.com/reference/sending-api-requests.html


* https://api-dev.smart-connect.cloud/POS (development)
* https://api.smart-connect.cloud/POS (production)
