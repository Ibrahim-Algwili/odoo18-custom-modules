{
    'name': "Vendor Relationship Management (VRM)",
    'version' : "1.0",
    'author' : "Ibrahim Algwili",
    'category' : "Custom",
    'summary' : "VRM Custom Module",
    'depends' : ['base', 'mail', 'product' , 'contacts' , 'purchase'],

    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/window_actions.xml',
        'views/res_partner_views.xml',
        'views/purchase_team_views.xml',
        'views/vrm_vendor_lead_views.xml',
        'views/vrm_stage.xml',
        'views/vrm_tags.xml',
        'views/vrm_menu.xml',
        'wizard/suspend_reason_wizard_views.xml',
    ],
    'installable': True,
    'application': True,

}