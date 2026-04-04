# -*- coding: utf-8 -*-
{
    'name': "Hooks Module",
    'summary': "Short (1 phrase/line) summary of the module's purpose",
    'description': """
Long description of module's purpose
    """,
    'author': "My Company",
    'version': '0.1',
    'depends': ['base', 'contacts'],
    'data': [
    ],

    # ======================= HOOKS ============================

    #  your_method_name ---> Should be Provided int the __init__ file , or create hooks.py file

    # "pre_init_hook": "your_method_name",     -->    Before Installing The Module
    # "post_init_hook": "your_method_name",    -->    After Installing The Module
    # "uninstall_hook": "your_method_name",    -->    When Deleting The Module
    # "post_load": "your_method_name",         -->    When Server Load

    "pre_init_hook": "_hemo_pre_init_hook",
    "post_init_hook": "_hemo_post_init_hook",
    "uninstall_hook": "_hemo_uninstall_hook",
    "post_load": "",
}
