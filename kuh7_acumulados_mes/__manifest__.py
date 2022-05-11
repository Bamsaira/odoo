# -*- coding: utf-8 -*-
{
    'name': 'KUH7 - Generar acumulados del mes',
    'summary': 'Agregar campos con acumulados del mes',
    'description': '''
    * Obtener acumulados del mes para finiquitos
    ''',
    "website": "http://kuh7.mx",
    'author': 'Kuh7 Soluciones S.A. de C.V.',
    'version': '1.2',
    'category': 'payslip',
    'depends': [
        'nomina_cfdi_ee'
    ],
    'data': [
        'views/hr_payslip_view.xml'
    ],
    'installable': True,
    'application': False
}