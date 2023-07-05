# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime

# manejo de excepciones
from odoo.exceptions import AccessError, MissingError, ValidationError


# crear los procesos de votación
class ProcesoVotaciones(models.Model):
    _name = 'proceso.votaciones'
    _description = 'Proceso de Votación'
    _rec_name = 'descripcion'

    # Campos de la votación
    descripcion = fields.Text(string='Descripción')
    fecha_inicio = fields.Datetime(string='Fecha de Inicio', readonly=True)
    fecha_fin = fields.Datetime(string='Fecha de Fin', readonly=True)
    # le paso los candidatos a traves de un campo Many2many, ya que una Votacion puede tener muchos candidatos, y un candidato puede estar en muchas Votaciones
    candidatos = fields.Many2many('res.partner', string='Candidatos', domain=[('tipo_persona', '=', 'candidato')])
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('en_proceso', 'En Proceso'),
        ('cerrada', 'Cerrada')
    ], string='Estado', default='borrador')#, compute='_verificar_sede_estudio')

    # Relación One2many con el modelo 'registro.votos'
    votos_registrados = fields.One2many('registro.votos', 'proceso_votacion_seleccionado_objeto', string='Votos Registrados')

    sede_estudio_del_estudiante = fields.Many2one('sedes.universidad', string='Sede de Estudio', required=True)

    @api.model_create_multi
    def create(self, vals):
        print("CREATE\n", "vals: ", vals, "self: ", self)

        id_sede = 0

        #si no hay una sede aun creada en el modelo de sedes de la universidad, cuando se está importando
        #if not 'sede_estudio_del_estudiante' in vals[0]:
        if type(vals[0]['sede_estudio_del_estudiante']) != int:
            print("entra aqui")
            # crear la sede en el modelo de sedes de la universidad
            nombre_sede = vals[0]['sede_estudio_del_estudiante']
            fecha_inicio_import = datetime.strptime(str(vals[0]['fecha_inicio']), '%Y-%m-%d %H:%M:%S')
            fecha_final_import = datetime.strptime(str(vals[0]['fecha_fin']), '%Y-%m-%d %H:%M:%S')
            print("nombre de la sede: ", nombre_sede, fecha_inicio_import, fecha_final_import)

            #para que no vuelva a crear la misma sede:
            busco_la_sede = self.env['sedes.universidad'].sudo().search([('nombre_sede', '=', nombre_sede)])
            payload = ({
                    'nombre_sede': nombre_sede,
                    'fecha_inicio':fecha_inicio_import,
                    'fecha_fin': fecha_final_import
                })

            if busco_la_sede:
                print("actualiza la sede..")
                busco_la_sede.write(payload)
            else:
                print("\n crea la sede..")
                creados = self.env['sedes.universidad'].sudo().create(payload)

            #luego el busca esa sede nuevamente, para poder sacar su id
            sede_creada_id = self.env['sedes.universidad'].sudo().search([('nombre_sede','=',nombre_sede)],
                                                                      order='create_date DESC', limit=1)
            id_sede = sede_creada_id.id
            print("id sede creada apartir de importación: ", id_sede, "nombre sede: ", sede_creada_id.nombre_sede)
            vals[0]['sede_estudio_del_estudiante'] = id_sede

        #aqui la sede ya existe, osea esto es cuando se crea un registro desde la interfaz de odoo
        else:
            print("hay una sede con ese id")
            id_sede = int(vals[0]['sede_estudio_del_estudiante'])

        print("id sede con el que se empieza el flujo: ", id_sede)
        sede_existente = self.env['sedes.universidad'].search([('id', '=', id_sede)])
        print("sede: ", sede_existente)
        mantener_estado = vals[0]['estado']

        fecha_inicio_sede = sede_existente.fecha_inicio
        fecha_fin_sede = sede_existente.fecha_fin
        print("\nfecha inicio sede: ", fecha_inicio_sede, type(fecha_inicio_sede), "fecha fin sede: ", fecha_fin_sede, type(fecha_fin_sede))
        fecha_actual_votacion = fields.Datetime.now()
        print("fecha actual: ", fecha_actual_votacion)
        if fecha_inicio_sede < fecha_actual_votacion and fecha_actual_votacion < fecha_fin_sede:
            vals[0]['estado'] = mantener_estado
        elif fecha_inicio_sede > fecha_actual_votacion and fecha_actual_votacion < fecha_fin_sede:
            vals[0]['estado'] = 'borrador'
        else:
            vals[0]['estado'] = 'cerrada'

        #controlar fechas que se ingresan, para validar si por ejemplo la fechca inicial ingresada es menor a la del padre, que en este caso seria la de la sede
        #esto para cuando se va a importar las fechas del excel

        #esto si las fechas se crean desde la interfaz del odoo, si las fechas ya tienen algo entonces no hay necesidad de hacer esto
        vals[0]['fecha_inicio'] = str(fecha_inicio_sede)
        vals[0]['fecha_fin'] = str(fecha_fin_sede)

        fecha_inicial_ingresada = vals[0]['fecha_inicio']
        fecha_final_ingresada = vals[0]['fecha_fin']
        fecha_inicial_ingresada = datetime.strptime(fecha_inicial_ingresada, '%Y-%m-%d %H:%M:%S')
        fecha_final_ingresada = datetime.strptime(fecha_final_ingresada, '%Y-%m-%d %H:%M:%S')

        print("fecha inicio ingresada: ",fecha_inicial_ingresada, type(fecha_inicial_ingresada)," - fecha final ingresada: ", fecha_final_ingresada, type(fecha_final_ingresada))

        if fecha_inicial_ingresada and fecha_final_ingresada:
            if fecha_inicial_ingresada < fecha_inicio_sede:
                # la fecha de inicio ingresada es menor a fecha de inicio de la sede, por tanto la fecha de inicio que se debe mantener es la fecha de la sede
                vals[0]['fecha_inicio'] = fecha_inicio_sede
            if fecha_final_ingresada > fecha_fin_sede:
                #si la fecha final ingresada es mayor a la de la sede, pues se debe mantener la de la sede
                vals[0]['fecha_fin'] = fecha_fin_sede

        print("vals: ", vals)

        res = super(ProcesoVotaciones, self).create(vals)
        return res

    def write(self, vals):

        print("WRITE\n", "vals: ", vals, "self: ", self)

        for rec in self:

            if 'sede_estudio_del_estudiante' in vals:
                id_sede = int(vals.get('sede_estudio_del_estudiante'))
                sede_existente = self.env['sedes.universidad'].search([('id', '=', id_sede)])
                print("sede: ", sede_existente)

                #estado = self.search([('id', '=', self.id)]).estado
                estado = rec.estado
                print("estado: ", estado)

                fecha_inicio_sede = sede_existente.fecha_inicio
                fecha_fin_sede = sede_existente.fecha_fin
                print("\nfecha inicio: ", fecha_inicio_sede, "fecha fin: ", fecha_fin_sede)
                fecha_actual_votacion = fields.Datetime.now()
                print("fecha actual: ", fecha_actual_votacion)
                if fecha_inicio_sede < fecha_actual_votacion and fecha_actual_votacion < fecha_fin_sede:
                    rec.estado = estado
                else:
                    rec.estado = 'cerrada'

                #asigno los valores de la sede:
                rec.fecha_inicio = fecha_inicio_sede
                print("fecha de inicio que va a quedar: ", rec.fecha_inicio, type(rec.fecha_inicio))
                rec.fecha_fin = fecha_fin_sede
                print("fecha de fin que va a quedar: ", rec.fecha_fin, type(rec.fecha_fin))

        result = super(ProcesoVotaciones, self).write(vals)
        return result

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

    #boton que inicia la accion que contiene ejecuta la vista del wizard
    #def abrir_wizard_importacion(self):
    #    view_id = self.env.ref('ges_votaciones.action_wizard_importar')
    #    action = view_id.read()[0]
    #    return action

    @api.constrains('fecha_inicio', 'fecha_fin')
    def date_constrains(self):
        for rec in self:
            if rec.fecha_fin < rec.fecha_inicio:
                raise ValidationError('Lo sentimos, la fecha final debe ser mayor que la fecha de inicio')

# modelo para registrar los votos
class registro_votos(models.Model):
    _name = 'registro.votos'
    _description = 'Registrar Votos'

    #conexion con modelo proceso.votaciones
    proceso_votacion_seleccionado_objeto = fields.Many2one('proceso.votaciones', string="contiene el objeto proceso_votacion")

    proceso_votacion_seleccionado = fields.Char(string='Proceso de Votacion Seleccionado')
    candidato_seleccionado = fields.Char(string='Candidato Seleccionado')
    votos = fields.Integer(string='Cantidad de Votos')
    foto_candidato = fields.Binary(string='Foto del Candidato')
