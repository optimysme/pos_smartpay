# -*- coding: utf-8 -*-
{
    "name": "Smartpay POS integration",
    "version": "1.0",
    "sequence": 1,
    "category": "POS",
    "depends": [
        "point_of_sale",
        "website",  # to handle multi-website configurations
    ],
    "author": "Solnet Solutions Ltd",
    "website": "https://www.solnet.co.nz",
    "description": 
"""
    Smartpay POS Integration
    ========================

    This module integrates Smartpay POS terminals with Odoo's POS
    module.

    Endpoints are configured into the rc files::

    [pos_smartpay]
    endpoint = https://api.smart-connect.cloud/POS
    
    Possible *endpoint* values are currently:

    * https://api-dev.smart-connect.cloud/POS (development)
    * https://api.smart-connect.cloud/POS (production)
""",
    "data": [
        "views/pos-dashboard.xml",
        "views/pos-assets.xml",
        "wizards/smartpay_pairing.xml",
        "wizards/smartpay_tx.xml",
    ],
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "active": False,
}
