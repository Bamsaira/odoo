# -*- coding: utf-8 -*-
{
    'name': 'KUH7 - Dealba Custom',
    'summary': 'KUH7 - Dealba Custom',
    'description': '''
    KUH7 - Dealba Custom
    ''',
    "website": "https://www.kuh7.mx/",
    'author': 'KUH7 SOLUCIONES S.A. de C.V.',
    'version': '1.0',
    'category': 'Dealba',
    'depends': [
        'project',
        'hr',
        'sale_management',
        'sale_project',
        'mrp_workorder',
        'purchase',
    ],
    'data': [
        'data/project_task_type_data.xml',
        'data/cron_data.xml',
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/project_views.xml',
        'views/assets.xml',
        'report/report_proyecto_avance.xml',
        'views/mrp_workcenter_views.xml',
        'views/mrp_workorder_views.xml',
        'views/mrp_views.xml',
    ],
}