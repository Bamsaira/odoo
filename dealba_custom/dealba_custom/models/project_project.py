# -*- coding: utf-8 -*-

import pytz

from datetime import datetime

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.depends('task_count')
    def _compute_tot_fases_acciones(self):
        for record in self:
            for fase in record.fase_ids:
                record.fase_ids = [(2, fase.id)]
            for accion in record.accion_ids:
                record.accion_ids = [(2, accion.id)]
            task_type_ids = self.env['project.task.type'].search([
                ('project_ids', 'in', record.ids)
            ])
            for task_type_id in task_type_ids:
                record.fase_ids = [(0, 0, {
                    'project_id': record.id,
                    'name': task_type_id.name,
                    'estilo': 'titulo',
                })]
                tarea_ids = self.env['project.task'].search([
                    ('project_id', '=', record.id),
                    ('stage_id', '=', task_type_id.id),
                ])
                for tarea_id in tarea_ids:
                    gyr = False
                    fch_programa = False
                    fch_cierre = False
                    contacto_id = False
                    task_id = False
                    es_padre = tarea_ids.filtered(lambda x: x.parent_id == tarea_id)
                    if not es_padre:
                        if tarea_id.kanban_state == 'normal':
                            gyr = 'G'
                        elif tarea_id.kanban_state == 'done':
                            gyr = 'Y'
                        else:
                            gyr = 'R'
                        fch_programa = tarea_id.date_deadline
                        fch_cierre = tarea_id.fch_cierre
                        contacto_id = tarea_id.contacto_id.id
                        task_id = tarea_id.id
                    record.fase_ids = [(0, 0, {
                        'project_id': record.id,
                        'name': tarea_id.name,
                        'gyr': gyr,
                        'fch_programa': fch_programa,
                        'fch_cierre': fch_cierre,
                        'contacto_id': contacto_id,
                        'task_id': task_id,
                    })]
                    for accion in tarea_id.accion_ids:
                        record.accion_ids = [(0, 0, {
                            'project_id': record.id,
                            'task_type_id': task_type_id.id,
                            'task_id': accion.task_id.id,
                            'actividad': accion.actividad,
                            'fch': accion.fch,
                            'no_conformidad': accion.no_conformidad,
                            'plan_accion': accion.plan_accion,
                            'fch_compromiso': accion.fch_compromiso,
                            'contacto_id': accion.contacto_id.id,
                            'status': accion.status,
                        })]
            record.tot_fases_acciones = 1

    @api.depends('fch_inicio', 'fch_fin')
    def _compute_semanas(self):
        for record in self:
            if record.fch_inicio and record.fch_fin:
                record.semanas = int(round((record.fch_fin - record.fch_inicio).days / 7, 0))
            else:
                record.semanas = 0

    label_tasks = fields.Char(default='Elementos APQP')
    no_especificacion = fields.Char(string='No. Parte')
    num_especificacion = fields.Char(string='No. Especificación')
    rev_especificacion = fields.Date(string='Rev. Especificación')
    ev_riesgo = fields.Char(string='Evaluación Riesgo')
    sitio = fields.Boolean(string='Sitio')
    tecnologia = fields.Boolean(string='Tecnología')
    proceso = fields.Boolean(string='Proceso')
    otro_riesgo = fields.Char(string='Otros Riesgos')
    oem = fields.Char(string='OEM')
    fch_inicio = fields.Date(string='Fecha Inicio')
    fch_fin = fields.Date(string='Fecha Finalización')
    fch_rev = fields.Date(string='Fecha Revisión')
    semanas = fields.Integer(
        string='Semanas',
        compute='_compute_semanas',
    )
    contacto_ids = fields.One2many(
        comodel_name='project.project.partner',
        inverse_name='project_id',
        string='Equipo de trabajo',
    )
    product_ids = fields.One2many(
        comodel_name='project.project.product',
        inverse_name='project_id',
        string='Productos',
    )
    fase_ids = fields.One2many(
        comodel_name='project.project.fase',
        inverse_name='project_id',
        string='Fases',
    )
    accion_ids = fields.One2many(
        comodel_name='project.project.accion',
        inverse_name='project_id',
        string='Acciones',
    )
    tot_fases_acciones = fields.Integer(
        compute='_compute_tot_fases_acciones',
    )
    plantilla = fields.Selection(selection=[
        ('proveedores', 'Proveedores'),  # Proveedores
        ('clientes', 'Clientes'),  # Biodiversidad
        ('blanco', 'En blanco'),  # Sin nada
    ], string='Plantilla')
    hito_ids = fields.One2many(
        comodel_name='project.project.hito',
        inverse_name='project_id',
        string='Hitos',
    )
    minuta_ids = fields.One2many(
        comodel_name='project.project.minuta',
        inverse_name='project_id',
        string='Minuta',
    )
    state = fields.Selection(selection=[
        ('Pendiente', 'Pendiente'),
        ('En tiempo', 'En tiempo'),
        ('Finalizado', 'Finalizado'),
        ('Atrasado', 'Atrasado'),
        ('Cancelado', 'Cancelado'),
    ], string='Estado', default='Pendiente')

    @api.model
    def create(self, vals):
        res = super(ProjectProject, self).create(vals)
        if 'plantilla' in vals:
            if vals['plantilla'] == 'proveedores':
                fase1_id = self.env.ref('dealba_custom.proveedor_fase_1')
                fase1_id.write({
                    'project_ids': [(4, res.id)]
                })
                self.env['project.task'].create({
                    'name': '1) Decisión de Abastecimiento',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 1,
                })
                elemento2 = self.env['project.task'].create({
                    'name': '2) Requisitos y Necesidades De Alba',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 2,
                })
                self.env['project.task'].create({
                    'name': '2.1) Diagrama de Flujo Preliminar',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 3,
                    'parent_id': elemento2.id,
                })
                self.env['project.task'].create({
                    'name': '2.2) Plan de Aseguramiento del Producto',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 4,
                    'parent_id': elemento2.id,
                })
                self.env['project.task'].create({
                    'name': '2.3) Comprensión de los CSRs',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 5,
                    'parent_id': elemento2.id,
                })
                self.env['project.task'].create({
                    'name': '3) Timing Plan',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 6,
                })
                fase2_id = self.env.ref('dealba_custom.proveedor_fase_2')
                fase2_id.write({
                    'project_ids': [(4, res.id)]
                })
                self.env['project.task'].create({
                    'name': '3) AMEF de Diseño',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 1,
                })
                self.env['project.task'].create({
                    'name': '4) Revisión del Diseño',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 2,
                })
                self.env['project.task'].create({
                    'name': '5) Plan de Verificación del Diseño',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 3,
                })
                self.env['project.task'].create({
                    'name': '6) Reporte de Estado APQP del Proveedor',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 4,
                })
                self.env['project.task'].create({
                    'name': '7) Istalaciones, Herramentales y Equipos',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 5,
                })
                self.env['project.task'].create({
                    'name': '8) Plan de Control de Prototipo',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 6,
                })
                self.env['project.task'].create({
                    'name': '9) Desarrollo del Prototipo',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 7,
                })
                self.env['project.task'].create({
                    'name': '10) Dibujos y Especificaciones',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 8,
                })
                self.env['project.task'].create({
                    'name': '11) Compromiso de Factibilidad del Equipo',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 9,
                })
                fase3_id = self.env.ref('dealba_custom.proveedor_fase_3')
                fase3_id.write({
                    'project_ids': [(4, res.id)]
                })
                self.env['project.task'].create({
                    'name': '12) Diagrama de Flujo del Proceso',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 1,
                })
                self.env['project.task'].create({
                    'name': '13) AMEF de Proceso',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 2,
                })
                self.env['project.task'].create({
                    'name': '14) Plan de Control de Pre-Lanzamiento',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 3,
                })
                self.env['project.task'].create({
                    'name': '15) Instrucciones del Proceso',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 4,
                })
                self.env['project.task'].create({
                    'name': '16) Estándar de Empaque',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 5,
                })
                fase4_id = self.env.ref('dealba_custom.proveedor_fase_4')
                fase4_id.write({
                    'project_ids': [(4, res.id)]
                })
                self.env['project.task'].create({
                    'name': '17) Plan de Control - Producción',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 1,
                })
                elemento18 = self.env['project.task'].create({
                    'name': '18) Corrida de Producción Significativa',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 2,
                })
                self.env['project.task'].create({
                    'name': '18.1) Auditoría de Proceso',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 3,
                    'parent_id': elemento18.id,
                })
                self.env['project.task'].create({
                    'name': '18.2) CQIs',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 4,
                    'parent_id': elemento18.id,
                })
                self.env['project.task'].create({
                    'name': '18.3) Run & Rate',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 5,
                    'parent_id': elemento18.id,
                })
                self.env['project.task'].create({
                    'name': '19) Estudio  Preliminar de la Capacidad del Proceso',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 6,
                })
                self.env['project.task'].create({
                    'name': '20) Evaluación del Sistema de Medición MSA',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 7,
                })
                self.env['project.task'].create({
                    'name': '21) Pruebas de Validación de la producción',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 8,
                })
                elemento22 = self.env['project.task'].create({
                    'name': '22) Part Submission Warrant',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 9,
                })
                self.env['project.task'].create({
                    'name': '22.1) Emisión PPAP',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 10,
                    'parent_id': elemento22.id,
                })
                self.env['project.task'].create({
                    'name': '22.2) Aprobación PPAP',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 11,
                    'parent_id': elemento22.id,
                })
                fase5_id = self.env.ref('dealba_custom.proveedor_fase_5')
                fase5_id.write({
                    'project_ids': [(4, res.id)]
                })
                self.env['project.task'].create({
                    'name': '23) Contención Anticipada del Producto EPC',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase5_id.id,
                    'sequence': 1,
                })
            elif vals['plantilla'] == 'clientes':
                fase1_id = self.env.ref('dealba_custom.cliente_fase_1')
                fase1_id.write({
                    'project_ids': [(4, res.id)]
                })
                elemento11 = self.env['project.task'].create({
                    'name': '1.1 Requisitos de Entrada',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 1,
                })
                self.env['project.task'].create({
                    'name': '1.1.1 Recolección de la Información',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 2,
                    'parent_id': elemento11.id,
                })
                self.env['project.task'].create({
                    'name': '1.1.3 Revisión de los Requisitos del Producto',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 3,
                    'parent_id': elemento11.id,
                })
                self.env['project.task'].create({
                    'name': '1.2 Compromiso de Factibilidad del Equipo',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase1_id.id,
                    'sequence': 4,
                })
                fase2_id = self.env.ref('dealba_custom.cliente_fase_2')
                fase2_id.write({
                    'project_ids': [(4, res.id)]
                })
                elemento21 = self.env['project.task'].create({
                    'name': '2.1 Instalaciones, Herramentales y Equipos',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 1,
                })
                self.env['project.task'].create({
                    'name': '2.1.6 Diseño de Herramentales Internos',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 2,
                    'parent_id': elemento21.id,
                })
                self.env['project.task'].create({
                    'name': '2.1.7 Herramentales Internos',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 3,
                    'parent_id': elemento21.id,
                })
                self.env['project.task'].create({
                    'name': '2.1.8 Herramentales Externos',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 4,
                    'parent_id': elemento21.id,
                })
                self.env['project.task'].create({
                    'name': '2.1.9 Validación de Herramentales',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 5,
                    'parent_id': elemento21.id,
                })
                self.env['project.task'].create({
                    'name': '2.2 Flujo del Proceso de Manufactura',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 6,
                })
                self.env['project.task'].create({
                    'name': '2.3 AMEF de Proceso',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 7,
                })
                self.env['project.task'].create({
                    'name': '2.4 Plan de Control Pre-Lanzamiento',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 8,
                })
                self.env['project.task'].create({
                    'name': '2.5 Instrucciones del Proceso',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 9,
                })
                self.env['project.task'].create({
                    'name': '2.6 Estándar de Empaque',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase2_id.id,
                    'sequence': 10,
                })
                fase3_id = self.env.ref('dealba_custom.cliente_fase_3')
                fase3_id.write({
                    'project_ids': [(4, res.id)]
                })
                elemento31 = self.env['project.task'].create({
                    'name': '3.1 Corrida de Producción Significativa',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 1,
                })
                self.env['project.task'].create({
                    'name': '3.1.2 Ajuste y Configuración del Equipo',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 2,
                    'parent_id': elemento31.id,
                })
                self.env['project.task'].create({
                    'name': '3.1.3 Proceso de Transformación',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 3,
                    'parent_id': elemento31.id,
                })
                self.env['project.task'].create({
                    'name': '3.1.4 Tratamientos Superficiales',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 4,
                    'parent_id': elemento31.id,
                })
                self.env['project.task'].create({
                    'name': '3.2 Estudios de la Capacidad Preliminar del Proceso SPC',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 5,
                })
                elemento34 = self.env['project.task'].create({
                    'name': '3.4 Pruebas de Validación del Proceso PVT',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 6,
                })
                self.env['project.task'].create({
                    'name': '3.4.1 Validación Dimensional',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 7,
                    'parent_id': elemento34.id,
                })
                self.env['project.task'].create({
                    'name': '3.4.2 Validación Funcional / Rendimiento',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 8,
                    'parent_id': elemento34.id,
                })
                self.env['project.task'].create({
                    'name': '3.5 Plan de Control Producción',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 9,
                })
                elemento37 = self.env['project.task'].create({
                    'name': '3.7 Part Submission Warrant',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 10,
                })
                self.env['project.task'].create({
                    'name': '3.7.2 PSW de Alba',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase3_id.id,
                    'sequence': 11,
                    'parent_id': elemento37.id,
                })
                fase4_id = self.env.ref('dealba_custom.cliente_fase_4')
                fase4_id.write({
                    'project_ids': [(4, res.id)]
                })
                self.env['project.task'].create({
                    'name': '4.1 Contención Anticipada del Producto EPC',
                    'company_id': self.env.company.id,
                    'project_id': res.id,
                    'stage_id': fase4_id.id,
                    'sequence': 1,
                })
            self.env['project.project.hito'].create({
                'project_id': res.id,
                'name': 'Kick Off',
            })
            self.env['project.project.hito'].create({
                'project_id': res.id,
                'name': 'Aprobación del programa',
            })
            self.env['project.project.hito'].create({
                'project_id': res.id,
                'name': 'Confirmación del proceso',
            })
            self.env['project.project.hito'].create({
                'project_id': res.id,
                'name': 'Pre-lanzamiento',
            })
            self.env['project.project.hito'].create({
                'project_id': res.id,
                'name': 'Confirmación de piezas PL',
            })
            self.env['project.project.hito'].create({
                'project_id': res.id,
                'name': 'Validación del producto y proceso',
            })
            self.env['project.project.hito'].create({
                'project_id': res.id,
                'name': 'Producción en serie',
            })
        return res

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref("dealba_custom.report_proyecto_avance")._render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()

    def canvas_hito_donuts(self):
        hito_tot_ids = self.hito_ids
        hito_proyecto_ids = hito_tot_ids.filtered(lambda x: x.status != False)
        hito_restante_ids = hito_tot_ids - hito_proyecto_ids
        hito_proy_porcentaje = round(len(hito_proyecto_ids) * 100 / len(hito_tot_ids), 0)
        hito_rest_porcentaje = round(len(hito_restante_ids) * 100 / len(hito_tot_ids), 0)
        hitos = ['Hitos del poyecto', 'Hitos restantes']
        valores = [hito_proy_porcentaje, hito_rest_porcentaje]
        return [hitos, valores]

    def canvas_hito_bar(self):
        hito_tot_ids = self.hito_ids
        hito_real_ids = hito_tot_ids.filtered(lambda x: x.status != False)
        hito_programado_ids = hito_tot_ids.filtered(lambda x: x.fch_programada != False)
        hito_real_porcentaje = round(len(hito_real_ids) * 100 / len(hito_tot_ids), 0)
        hito_programado_porcentaje = round(len(hito_programado_ids) * 100 / len(hito_tot_ids), 0)
        hitos = ['Avance real', 'Avance programado']
        valores = [hito_real_porcentaje, hito_programado_porcentaje]
        return [hitos, valores]

    def contar_fases(self):
        return len(self.fase_ids.filtered(lambda x: x.estilo == 'titulo'))

    def detalle_fases(self):
        task_type_ids = self.env['project.task.type'].search([
            ('project_ids', 'in', self.ids)
        ])
        consolidado = []
        hoy = datetime.now(pytz.timezone('America/Mexico_City')).date()
        for task_type_id in task_type_ids:
            data = []
            data.append(task_type_id.name)
            tarea_ids = self.env['project.task'].search([
                ('project_id', '=', self.id),
                ('stage_id', '=', task_type_id.id),
            ])
            elementos_ids = tarea_ids.filtered(lambda x: len(x.parent_id) == 0)
            data.append(str(len(elementos_ids)))
            actividades_ids = tarea_ids - tarea_ids.filtered(lambda x: x.parent_id != False).mapped('parent_id')
            data.append(str(len(actividades_ids)))
            fch_cierre_prog = sorted(list(filter(lambda elem: elem != False, actividades_ids.mapped('date_deadline'))), reverse=True)
            if fch_cierre_prog:
                fch_cierre_prog = fch_cierre_prog[0].strftime("%d-%m-%Y")
            else:
                fch_cierre_prog = ""
            data.append(fch_cierre_prog)
            actividades_restantes_ids = actividades_ids.filtered(lambda x: x.fch_cierre == False)
            if actividades_restantes_ids:
                status = "Abierta"
            else:
                status = "Cerrada"
            data.append(status)
            actividades_cerradas_ids = actividades_ids - actividades_restantes_ids
            data.append(str(len(actividades_cerradas_ids)))
            data.append(str(len(actividades_restantes_ids)))
            actividades_retrasas_ids = actividades_restantes_ids.filtered(lambda x: x.date_deadline != False and x.date_deadline < hoy)
            data.append(str(len(actividades_retrasas_ids)))
            avance_porcentaje = int(round(len(actividades_cerradas_ids) * 100 / len(actividades_ids), 0))
            data.append("{0} %".format(str(avance_porcentaje)))
            acciones_abiertas_ids = actividades_restantes_ids.mapped('accion_ids')
            data.append(str(len(acciones_abiertas_ids)))
            if len(actividades_restantes_ids) == 0:
                fch_cierre_real = sorted(list(filter(lambda elem: elem != False, actividades_ids.mapped('fch_cierre'))), reverse=True)[0].strftime("%d-%m-%Y")
            else:
                fch_cierre_real = ""
            data.append(fch_cierre_real)
            consolidado.append(data)
        return consolidado

    def data_fases(self):
        task_type_ids = self.env['project.task.type'].search([
            ('project_ids', 'in', self.ids)
        ])
        data_fases = {}
        nombres = ['Retraso', 'Avance real', 'Avance programado']
        hoy = datetime.now(pytz.timezone('America/Mexico_City')).date()
        for num, task_type_id in enumerate(task_type_ids):
            tarea_ids = self.env['project.task'].search([
                ('project_id', '=', self.id),
                ('stage_id', '=', task_type_id.id),
            ])
            actividades_ids = tarea_ids - tarea_ids.filtered(lambda x: x.parent_id != False).mapped('parent_id')
            actividades_programadas = actividades_ids.filtered(lambda x: x.date_deadline != False)
            if actividades_programadas:
                programado = int(round(len(actividades_programadas) * 100 / len(actividades_ids), 0))
                actividades_terminadas = actividades_programadas.filtered(lambda x: x.fch_cierre != False)
                real = int(round(len(actividades_terminadas) * 100 / len(actividades_ids), 0))
                actividades_retrasas_ids = actividades_programadas.filtered(lambda x: x.fch_cierre == False and x.date_deadline < hoy)
                retrasado = int(round(len(actividades_retrasas_ids) * 100 / len(actividades_ids), 0))
                data = [retrasado, real, programado]
            else:
                data = [0, 0, 0]
            data_fases['ctx_{0}'.format(str(num + 1))] = [nombres, data]
        return data_fases

    def canvas_avance_proyecto(self):
        tarea_ids = self.env['project.task'].search([
            ('project_id', '=', self.id),
        ])
        actividades_ids = tarea_ids - tarea_ids.filtered(lambda x: x.parent_id != False).mapped('parent_id')
        actividades_programadas = actividades_ids.filtered(lambda x: x.date_deadline != False)
        if actividades_programadas:
            proyecto_programado_porcentaje = int(round(len(actividades_programadas) * 100 / len(actividades_ids), 0))
            actividades_terminadas = actividades_programadas.filtered(lambda x: x.fch_cierre != False)
            proyecto_real_porcentaje = int(round(len(actividades_terminadas) * 100 / len(actividades_ids), 0))
        else:
            proyecto_real_porcentaje = 0
            proyecto_programado_porcentaje = 0
        proyecto = ['Avance real', 'Avance programado']
        valores = [proyecto_real_porcentaje, proyecto_programado_porcentaje]
        return [proyecto, valores]

    def iniciar(self):
        self.state = 'En tiempo'

    def cancelar(self):
        self.state = 'Cancelado'

    def inicio_proyecto_cron(self):
        project_ids = self.search([
            ('state', '=', 'Pendiente'),
            ('fch_inicio', '<=', fields.Date.today()),
        ])
        for project_id in project_ids:
            project_id.state = 'En tiempo'

    def finalizar(self):
        self.state = 'Finalizado'

    def atrasado(self):
        self.state = 'Atrasado'

    def finalizar_proyecto_cron(self):
        project_ids = self.search([
            ('state', 'in', ['En tiempo', 'Atrasado']),
        ])
        for project_id in project_ids:
            hito_tot_ids = project_id.hito_ids
            hito_pendiente_ids = project_id.hito_ids.filtered(lambda x: x.status != False)
            if not hito_tot_ids - hito_pendiente_ids:
                project_id.state = 'Finalizado'

    def atrasado_proyecto_cron(self):
        project_ids = self.search([
            ('state', '=', 'En tiempo'),
            ('fch_fin', '<=', fields.Date.today())
        ])
        for project_id in project_ids:
            hito_pendiente_ids = project_id.hito_ids.filtered(lambda x: x.status == False)
            if hito_pendiente_ids:
                project_id.state = 'Atrasado'


class ProjectProjectPartner(models.Model):
    _name = "project.project.partner"

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
    )
    contacto_id = fields.Many2one(
        comodel_name='res.partner',
        string='Miembros del Equipo',
    )
    company_id = fields.Many2one(
        comodel_name='res.partner',
        string='Compañía',
    )
    job_title = fields.Char(string='Función')
    phone_two = fields.Char(string='Teléfono')
    private_email = fields.Char(string='E-mail')

    @api.onchange('contacto_id')
    def _onchange_contacto_id(self):
        self.company_id = False
        self.job_title = False
        self.phone_two = False
        self.private_email = False
        if self.contacto_id:
            self.company_id = self.contacto_id.parent_id
            self.job_title = self.contacto_id.function
            self.phone_two = self.contacto_id.phone
            self.private_email = self.contacto_id.email


class ProjectProjectProduct(models.Model):
    _name = "project.project.product"

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
    )
    nivel = fields.Selection(selection=[
        ('prototipo', 'Prototipo'),
        ('prelanzamiento', 'Pre-Lanzamiento'),
        ('produccion', 'Producción'),
    ], string='Nivel de Producto')
    fch = fields.Date(string='Fecha')
    ctd = fields.Float(string='Cantidad')
    comentario = fields.Char(string='Comentario')


class ProjectProjectFase(models.Model):
    _name = "project.project.fase"

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
    )
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Tarea'
    )
    name = fields.Char(string='Elementos APQP')
    gyr = fields.Selection(selection=[
        ('G', 'G'),
        ('Y', 'Y'),
        ('R', 'R'),
    ], string='GYR')
    fch_programa = fields.Date(string='Fecha programa')
    fch_cierre = fields.Date(string='Fecha cierre')
    contacto_id = fields.Many2one(
        comodel_name='res.partner',
        string='Responsable',
    )
    archivo = fields.Binary(
        related='task_id.archivo',
        string='Entregable',
    )
    archivo_filename = fields.Char(
        related='task_id.archivo_filename',
        string='Nombre entregable',
    )
    estilo = fields.Char(string='Estilo')


class ProjectProjectAccion(models.Model):
    _name = "project.project.accion"

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
    )
    task_type_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Fase APQP'
    )
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Elemento'
    )
    actividad = fields.Char(string='Actividad')
    fch = fields.Date(string='Fecha')
    no_conformidad = fields.Char(string='No Conformidad')
    plan_accion = fields.Char(string='Plan de Acción')
    fch_compromiso = fields.Date(string='Fecha compromiso')
    contacto_id = fields.Many2one(
        comodel_name='res.partner',
        string='Responsable',
    )
    status = fields.Selection(selection=[
        ('G', 'G'),
        ('Y', 'Y'),
        ('R', 'R'),
    ], string='Status')


class ProjectProjectHito(models.Model):
    _name = "project.project.hito"

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
    )
    name = fields.Char(string='Hito')
    fch_programada = fields.Date(string='Fecha programada')
    fch_real = fields.Date(string='Fecha real')
    status = fields.Selection(selection=[
        ('G', 'G'),
        ('Y', 'Y'),
        ('R', 'R'),
    ], string='Status')


class ProjectProjectMinuta(models.Model):
    _name = "project.project.minuta"

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
    )
    name = fields.Date(string='Fecha')
    contacto_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Asistentes',
    )
    compromiso = fields.Char(string='Compromisos')
    status = fields.Selection(selection=[
        ('Realizado', 'Realizado'),
        ('No realizado', 'No realizado'),
    ], string='Status')
