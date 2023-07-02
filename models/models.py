# -*- coding: utf-8 -*-

from odoo import models, fields, api

#manejo de errores:
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


# crear estudiantes y candidatos ( heredando de res.partner)
class EstudiantesYCandidatosUniversidad(models.Model):
    _inherit = 'res.partner'

    # Campos personalizados
    carrera_del_estudiante = fields.Char(string='Carrera del Estudiante')
    sede_estudio_del_estudiante = fields.Many2one('sedes.universidad', string='Sede de Estudio',
                                                  domain="[('ubicacion_sede', '=', country_name)]")
    country_name = fields.Integer(string='Nombre del País', related='country_id.id', readonly=True)
    vat = fields.Char("Número de Identificación Custom")
    tipo_persona = fields.Selection([
        ('estudiante', 'Estudiante'),
        ('candidato', 'Candidato')],
        string='Tipo de Persona', default='')
    votos = fields.One2many('proceso.votaciones', 'candidatos', string='Votos')

    # Funciones

    #se actualiza dinamicamente el valor del campo country_name una vez se modifique el campo country_id
    @api.onchange('country_id')
    def _onchange_country_id(self):
        for rec in self:
            if rec.country_id:
                print("nombre del pais: ",rec.country_id.name)
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
            print("candidato: ",contacto,"candidato existente: ", contacto_existente)
            if contacto_existente:
                raise ValidationError("Ya existe una persona con el mismo número de identificación.")

#crear los procesos de votaciones
class ProcesoVotaciones(models.Model):
    _name = 'proceso.votaciones'
    _description = 'Proceso de Votación'
    _rec_name = 'descripcion'

    # Campos de la votación
    descripcion = fields.Text(string='Descripción')
    fecha_inicio = fields.Datetime(string='Fecha de Inicio')
    fecha_fin = fields.Datetime(string='Fecha de Fin')
    # le paso los candidatos a traves de un campo Many2many, ya que una Votacion puede tener muchos candidatos, y un candidato puede estar en muchas Votaciones
    candidatos = fields.Many2many('res.partner', string='Candidatos', domain=[('tipo_persona', '=', 'candidato')])
    #cantidad_votos = fields.Integer(string='Cantidad de Votos')#, compute='_compute_cantidad_votos')
    foto_candidato = fields.Binary(string='Foto del Candidato') # la foto del candidato hay que traerla tambien de acuerdo al candidato que se seleccione ARREGLAR
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('en_proceso', 'En Proceso'),
        ('cerrada', 'Cerrada')
    ], string='Estado', default='borrador')

    #votos_candidatos = fields.One2many('proceso.votaciones.votos', 'votacion_id', string='Cantidad de Votos por Candidato')

    # Acciones para cambiar el estado de la votación
    #def action_iniciar_votacion(self):
    #    self.estado = 'en_proceso'

    #votacion iniciada o en proceso, posterior a cuando se ha creado
    def votacion_en_proceso(self):
        registros=0
        for record in self:
            if record.estado == 'borrador':
                record.estado = 'en_proceso'
                registros= registros + 1
        notificacion='Votaciones en proceso '+str(registros)
        print(notificacion)

    #votacion finalizada o cerrada, posterior a cuando se ha iniciado
    def votacion_cerrada(self):
        registros = 0
        for record in self:
            if record.estado == 'en_proceso':
                record.estado = 'cerrada'
                registros = registros + 1
        notificacion = 'Votaciones cerradas ' + str(registros)
        print(notificacion)

    #votacion en borrador, posterior a ser cerrada o iniciada
    def votacion_en_borrador(self):
        registros = 0
        for record in self:
            if record.estado == 'en_proceso' or record.estado == 'cerrada':
                record.estado = 'borrador'
                registros = registros + 1
        notificacion = 'Votaciones en borrador ' + str(registros)
        print(notificacion)

#modelo para registrar los votos
class registro_votos(models.Model):
    _name = 'registro.votos'
    _description = 'Registrar Votos'

    proceso_votacion_seleccionado = fields.Char(string='Proceso de Votacion Seleccionado')
    candidato_seleccionado = fields.Char(string='Candidato Seleccionado')
    votos = fields.Integer(string='Cantidad de Votos')

