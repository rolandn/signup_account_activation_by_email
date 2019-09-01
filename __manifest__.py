# -*- coding: utf-8 -*-

{
    "name": "Account Activate by email at signup",
    "summary": "Email confirmation to activation link",
    "version": "1.0",
    "category": "Authentication",
    'license': 'OPL-1',
    "author": "Kanak Infosystems LLP.",
    'website': 'https://kanakinfosystems.com',
    'images': ['static/description/banner.jpg'],
    "depends": ["website", "auth_signup"],
    "data": [
        "data/auth_signup_data.xml",
        "views/signup_templates.xml",
    ],
    "external_dependencies": {
        "python": [
            "validate_email",
        ],
    },
    'installable': True,
    'price': 30,
    'currency': 'EUR',
}
