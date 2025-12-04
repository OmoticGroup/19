# -*- coding: utf-8 -*-
# Copyright (C) 2025 Codusic Technology
# All Rights Reserved.
#
# This module is developed and maintained by Codusic Technology.
# You may not use, distribute, or modify this code without permission.
#
# Author: Codusic Technology

{
    'name': 'Website Hide Powered By Odoo Message',
    'version': '18.0.1.0.0',
    'summary': "Hide or remove the 'Powered by Odoo' message from your website footer easily without modifying core files.",
    'description': """
    This module allows you to hide or remove the default "Powered by Odoo" message displayed in the website footer.
    It helps make your website look more professional and aligned with your brand identity without changing core code.
    
    Key Features:
    - Hide the “Powered by Odoo” footer message with one click.
    - No modification of core or theme files required.
    - Compatible with all Odoo website themes.
    - Lightweight and performance-friendly.
    """,
    'author': 'Codusic Technology',
    'category': 'eCommerce',
    'depends': ['base', 'web', 'website', 'website_sale'],
    'data': [
        'views/hide_powered_by_odoo_message.xml',
    ],
    'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
