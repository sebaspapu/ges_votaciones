# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime

# manejo de excepciones
from odoo.exceptions import AccessError, MissingError, ValidationError

#heredo de res config settings
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    creador = fields.Char(string=' ', config_parameter='ges_votaciones.creador',
                       default='Sebastian Bolaños Morales', readonly=True)

# crear sedes de la universidad
class SedesUniversidad(models.Model):
    _name = 'sedes.universidad'
    _description = 'Sedes de la Universidad'
    _order = 'create_date ASC'
    _rec_name = 'nombre_sede'

    nombre_sede = fields.Char(string="Nombre de la Sede")
    ubicacion_sede = fields.Many2one('res.country', string="Ubicación")
    universidad_principal = fields.Char(string="Universidad", default='UNIACME')

    fecha_inicio = fields.Datetime(string='Inicio Procesos de Votación', required=True)
    fecha_fin = fields.Datetime(string='Fin Procesos de Votación', required=True)

    @api.constrains('fecha_inicio', 'fecha_fin')
    def date_constrains(self):
        for rec in self:
            if rec.fecha_fin < rec.fecha_inicio:
                raise ValidationError('Lo sentimos, la fecha final debe ser mayor que la fecha de inicio')

# crear estudiantes y candidatos ( heredando de res.partner)
class EstudiantesYCandidatosUniversidad(models.Model):
    _inherit = 'res.partner'

    # Campos personalizados
    carrera_del_estudiante = fields.Char(string='Carrera del Estudiante')
    sede_estudio_del_estudiante = fields.Many2one('sedes.universidad', string='Sede de Estudio',
                                                  domain="[('ubicacion_sede', '=', country_name)]")
    country_name = fields.Integer(string='Nombre del País', related='country_id.id', readonly=True)
    country_id = fields.Many2one(required=True, default=49)
    vat = fields.Char("Número de Identificación Custom", required=True)
    tipo_persona = fields.Selection([
        ('estudiante', 'Estudiante'),
        ('candidato', 'Candidato')],
        string='Tipo de Persona', default='', required=True)
    votos = fields.One2many('proceso.votaciones', 'candidatos', string='Votos')

    voto_realizado = fields.Selection([
        ('si', 'SI'),
        ('no', 'NO')], string="¿Ha participado en un proceso de votación?", default='no')

    # Funciones

    #se actualiza dinamicamente el valor del campo country_name una vez se modifique el campo country_id
    @api.onchange('country_id')
    def _onchange_country_id(self):
        for rec in self:
            if rec.country_id:
                #print("nombre del pais: ",rec.country_id.name)
                rec.country_name = rec.country_id.id
            else:
                rec.country_name = False

    @api.constrains('vat')
    def _verificar_numero_identidad(self):
        for contacto in self:
            #busca si el numero vat ingresado se encuentra dentro de de los registros ya existentes,
            #busca y compara el id del nuevo registro con el que ya existe, y si verifica que es diferente, quiere decir que se está
            #intentando crear un nuevo contacto, ya que el id es diferente
            contacto_existente = self.env['res.partner'].search(
                [('vat', '=', contacto.vat), ('id', '!=', contacto.id)])
            #print("candidato: ",contacto,"candidato existente: ", contacto_existente)
            if contacto_existente:
                raise ValidationError("Ya existe una persona con el mismo número de identificación.")