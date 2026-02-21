# -*- coding: utf-8 -*-
{
    "name": "Student",
    "summary": "Short (1 phrase/line) summary of the module's purpose",
    "license": "LGPL-3",
    "description": """
Long description of module's purpose
    """,
    "author": "Ibrahim Ali",
    "category": "Uncategorized",
    "version": "0.1",
    "depends": ["base", "mail", "contacts"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/student.student.csv",
        # 'data/res.partner.csv',
        # 'data/partner_data.xml',
        "data/student_data.xml",
        "views/views.xml",
    ],

    "installable": True,
    "auto_install": False,

}
