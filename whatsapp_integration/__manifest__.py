# -*- coding: utf-8 -*-
{
    "name": "Whatsapp Integration",
    "summary": "",
    "license": "LGPL-3",
    "description": """
    """,
    "author": "Ibrahim Ali",
    "category": "Uncategorized",
    "version": "0.1",
    "depends": ["base", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "wizards/send_whatsapp_message_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
