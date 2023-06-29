# -*- coding: utf-8 -*-
{
    'name': "ges_votaciones",

    'summary': """Sistema de Votaciones""",

    'description': """
        Permite gestionar y administrar un sistema de votaciones para diferentes sedes de una Universidad,
        Los Contactos ingresan a traves de un portal web, y realizan todo el proceso.
    """,

    'author': "Sebastián Bolaños Morales",
    'website': "https://github.com/sebaspapu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

