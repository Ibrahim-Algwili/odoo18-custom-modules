# -*- coding: utf-8 -*-
{
    "name": "Amount To Text",
    "summary": "",
    "license": "LGPL-3",
    "description": """
    """,
    "author": "Ibrahim Ali",
    "category": "Uncategorized",
    "version": "0.1",
    "depends": ["base", "sale", "web"],
    "data": [
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
        "reports/sale_order_report.xml",
        "reports/account_move_report.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'amount_to_text/static/src/css/amount_to_words.css',
        ],
    },
    "installable": True,
    "auto_install": False,
}
