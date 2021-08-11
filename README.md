# Smartpay POS Integration

This module integrates [Smartpay](https://smartpay.co.nz) POS terminals with Odoo's [POS module](https://www.odoo.com/app/point-of-sale-shop) via the API. Developed by [Solnet Solutions](https://solnet.co.nz).

### In scope:
- Pairing POS shop with the eftpos terminal. Supports 1 to 1 shop pairings
- Purchase handling
- Refund handling  
  
All other operations such as QR codes scanning, tipping, etc. are not supported.

## Server Configuration:
Endpoints are configured in the .rc files:

    [pos_smartpay]
	endpoint = https://api.smart-connect.cloud/POS
		
Possible *endpoint* values are available here: https://smartpaydev.com/reference/sending-api-requests.html


* https://api-dev.smart-connect.cloud/POS (development)
* https://api.smart-connect.cloud/POS (production)

## POS Setup  
- Point of Sale -> Configuration -> Payment Methods -> %your card payment method% -> Use a Payment Terminal - Select Smartpay  
- Associate that payment method with your POS shop  
- A new Pairing button (left) with the status (right) will appear on the shop tile  
![](https://github.com/ykya/pos_smartpay/raw/main/documentation/170018.png)  

## POS Usage  
1. Select a product and navigate to Payment screen  
2. Select the appropriate form of payment and click Send  
![](https://github.com/ykya/pos_smartpay/raw/main/documentation/170019.png)  

If the payment was successful, the status will change and you will be able to validate the order. If unsuccessfully, an error will be displayed with the message.  


## POS Error Handling
There are several error checks that have been built into the system:
- POS gets closed during the payment transaction being in progress - Reopen POS, click Payment and Click Send. The system will attempt to fetch the status of last transaction.
- Eftpos terminal power cut on Accepted payment screen - POS will fetch the latest update from the Smartpay API.
- Eftpos terminal power cut on Processing payment screen - POS will fetch the latest update from the Smartpay API.
