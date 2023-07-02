# -*- coding: utf-8 -*-
{
    'name': "Gestor Votaciones",

    'summary': 'Sistema de Votaciones',

    'description': """
        Permite gestionar y administrar un sistema de votaciones para diferentes sedes de una Universidad,
        Los Contactos ingresan a traves de un portal web, y realizan todo el proceso.""",

    'author': "Sebastián Bolaños Morales",
    'website': "https://github.com/sebaspapu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'contacts',
                'l10n_co',
                'website'
                ],

    # always loaded
    'data': [
        # archivo permiso de accesos
        'security/ir.model.access.csv',

        # vistas principales
        'views/sedes_and_inherit.xml',
        'views/proceso_votaciones.xml',
        'views/templates.xml',
        'views/res_config_settings.xml',
        'views/website_identificacion.xml',
        'views/website_votacion.xml',
        'views/registro_votos.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

