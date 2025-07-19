{
    'name': 'Estate',
    'installable': True,
    'application': True,
    'auto_install': False,
        'depends': [
            'base_setup'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/property_offer_views.xml',
        'views/property_type_views.xml',
        'views/property_tag_views.xml',
        'views/estate_menus.xml',
        'views/res_user_views.xml',
    ]
}