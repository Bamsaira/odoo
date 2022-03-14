# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.depends('project_id')
    def _compute_contacto_ids(self):
        for record in self:
            record.contacto_ids = [(6, 0, self.project_id.contacto_ids.mapped('contacto_id').ids)]

    contacto_id = fields.Many2one(
        comodel_name='res.partner',
        string='Responsable',
    )
    archivo = fields.Binary(string='Entregable')
    archivo_filename = fields.Char(string='Nombre entregable')
    status = fields.Selection(selection=[
        ('entregado', 'Entregado'),
        ('vencido', 'Vencido'),
    ], string='Status')
    fch_entrega = fields.Date(string='Fecha Entrega')
    evaluacion = fields.Selection(selection=[
        ('ok', 'Ok'),
        ('no_ok', 'No Ok'),
    ], string=u'Evaluación')
    fch_cierre = fields.Date(string='Fecha Cierre')
    accion_ids = fields.One2many(
        comodel_name='project.task.accion',
        inverse_name='task_id',
        string='Acciones'
    )
    contacto_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Equipo de trabajo',
        compute='_compute_contacto_ids'
    )
    comentario = fields.Char(string='Comentario')

    @api.onchange('project_id')
    def _onchange_project_id(self):
        dynamic_domain = {'contacto_id': [('id', 'in', self.project_id.contacto_ids.mapped('contacto_id').ids)]}
        return {'domain': dynamic_domain}


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    legend_normal = fields.Char(default='G')
    legend_done = fields.Char(default='Y')
    legend_blocked = fields.Char(default='R')


class ProjectTaskAccion(models.Model):
    _name = 'project.task.accion'

    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Elemento APQP',
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

    @api.onchange('actividad')
    def _onchange_actividad(self):
        dynamic_domain = {'contacto_id': [('id', 'in', self.task_id.project_id.contacto_ids.mapped('contacto_id').ids)]}
        return {'domain': dynamic_domain}
