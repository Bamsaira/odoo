# -*- coding: utf-8 -*-
{
    'name': 'KUH7 - Campos Especiales Nóminas',
    'summary': 'Cambio de campos requeridos para el ajuste de algunas reglas salariales en la nómina',
    'description': '''
    * Agregar campo de primer nomina trabajador
    ''',
    "website": "https://www.kuh7.mx/",
    'author': 'KUH7 SOLUCIONES S.A. DE C.V.',
    'version': '1.1',
    'category': 'payslip',
    'depends': [
        'nomina_cfdi_ee'
    ],
    'data': [
        'views/hr_payslip.xml'
    ],
    'installable': True,
    'application': False
}