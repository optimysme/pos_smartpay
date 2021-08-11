# Smartpay POS Integration

This module integrates [Smartpay](https://smartpay.co.nz) POS terminals with Odoo's [POS module](https://www.odoo.com/app/point-of-sale-shop). Developed by [Solnet Solutions](https://solnet.co.nz).

## In scope:
- Pairing shop with the eftpos terminal. Support 1 to 1 shop pairings
- Purchase handling
- Refund handling  
  
All other operations such as QR codes scanning, tipping etc are not supported.

## Server Configuration:
Endpoints are configured in the rc files:

    [pos_smartpay]
	endpoint = https://api.smart-connect.cloud/POS
		
Possible *endpoint* values are available here: https://smartpaydev.com/reference/sending-api-requests.html


* https://api-dev.smart-connect.cloud/POS (development)
* https://api.smart-connect.cloud/POS (production)

## POS Setup  
Point of Sale -> Configuration -> Payment Methods -> %your card payment method% -> Use a Payment Terminal - Select Smartpay  
Associate that payment method with your POS shop  
A new Pairing button will appear on the shop

ttete
