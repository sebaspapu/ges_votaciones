# -*- coding: utf-8 -*-
import odoo
from odoo import http
from odoo.http import request

class ProcesoVotacionSitioWeb(http.Controller):

    #creo una ruta para ingresar a la pestaña de identificacion, posterior a esto se redirecciona a el formulario de identificacion
    @http.route('/menu_identificacion', type="http", auth="public", website=True)
    def menu_identificacion_estudiante(self, **kwargs):
        return http.request.render('ges_votaciones.form_identificarse', {})

    #valido si el estudiante existe o no, tambien valido si el estudiante ya votó
    @http.route('/validacion/valido_identificacion', type="http", auth="public", website=True)
    def validacion_identificacion(self, **kwargs):

        numero_ident = int(kwargs.get('vat'))

        #ahora si vamos a buscar al contacto dentro del modelo de res.partner
        busqueda = request.env['res.partner'].sudo().search([('tipo_persona','=','estudiante')])

        plantilla_record = 'ges_votaciones.no_hay_estudiante_de_ese_tipo'

        if busqueda:
            for rec in busqueda:
                nume_iden_res = int(rec.vat)

                #buscar si el estudiante ya ha participado en un proceso de votacion
                estado_su_voto = rec.voto_realizado

                plantilla_record = 'ges_votaciones.estudiante_no_existente'

                if (numero_ident == nume_iden_res):

                    if estado_su_voto == 'no':

                        # buscar por el id la sede asociada
                        buscando_sede = rec.sede_estudio_del_estudiante
                        fecha_inicio_sede = buscando_sede.fecha_inicio
                        fecha_fin_sede = buscando_sede.fecha_fin
                        fecha_actual_votacion = odoo.fields.Datetime.now()
                        if fecha_inicio_sede < fecha_actual_votacion and fecha_actual_votacion < fecha_fin_sede:

                            # le envio el modelo que contiene todos los procesos de votacion
                            procesos_votacion_rec = request.env['proceso.votaciones'].sudo().search([])

                            # le envio el modelo que contiene todos los candidatos disponibles
                            candidatos_disponibles_rec = request.env['res.partner'].sudo().search(
                                [('tipo_persona', '=', 'candidato')])

                            if procesos_votacion_rec:
                                if candidatos_disponibles_rec:

                                    # le muestro un mensaje de que el estudiante se encuentra: (luego cambiara)
                                    return http.request.render('ges_votaciones.form_votacion', {
                                        'busqueda_num_id_rec': rec,
                                        'procesos_votacion_rec': procesos_votacion_rec,
                                        'candidatos_disponibles_rec': candidatos_disponibles_rec,
                                    })
                                else:
                                    plantilla_record = 'ges_votaciones.no_hay_candidatos_disponibles'
                                    break
                            else:
                                plantilla_record = 'ges_votaciones.no_hay_procesos_de_votacion'
                                break
                        elif fecha_actual_votacion < fecha_inicio_sede and fecha_actual_votacion < fecha_fin_sede:
                            plantilla_record = 'ges_votaciones.sede_fuera_de_rango_sin_iniciar'
                            break
                        else:
                            plantilla_record = 'ges_votaciones.sede_fuera_de_rango_finalizada'
                            break
                    else:
                        plantilla_record = 'ges_votaciones.estudiante_ha_votado'
                        break
                else:
                    plantilla_record = 'ges_votaciones.estudiante_no_existente'

        return http.request.render(plantilla_record, {})

    #pagina en donde se encuentra mi formulario para poder realizar el proceso de votación
    @http.route('/votacion/formulario', type="http", auth="public", website=True)
    def proceso_votacion(self, **kwargs):
        id_votacion_seleccionada = int(kwargs.get('id_votacion_seleccionada'))
        id_candidato_seleccionado = int(kwargs.get('id_candidato_seleccionado'))
        id_estudiante_votante = int(kwargs.get('busqueda_num_id_rec'))
        #primero realizo la validacion para saber si el candidato existe dentro de ese Proceso de votacion seleccionado
        procesos_votacion_rec = request.env['proceso.votaciones'].sudo().search([('id','=',id_votacion_seleccionada)])

        #busqueda estudiante
        busqueda_estudiante = request.env['res.partner'].sudo().search([('id', '=',id_estudiante_votante)])

        # buscar si el estudiante ya ha participado en un proceso de votacion
        estado_su_voto = busqueda_estudiante.voto_realizado

        #valido si el proceso de votación ya está cerrado

        estado_proceso = procesos_votacion_rec.estado

        if estado_proceso == 'en_proceso':

            cantidad_candidatos = procesos_votacion_rec.candidatos

            for rec_candidatos in cantidad_candidatos:
                if int(rec_candidatos.id) == id_candidato_seleccionado:

                    #busco el proceso de seleccion para ver si ya existe, y no volver a crear un mismo proceso
                    busqueda_proceso_votacion = request.env['registro.votos'].sudo().search([
                        ('proceso_votacion_seleccionado','=',procesos_votacion_rec.descripcion)])

                    bandera = False
                    voto = 1
                    foto_candidato = rec_candidatos.image_1920

                    if estado_su_voto == 'no':

                        # cambiar el estado de su voto
                        payload_voto = {
                           'voto_realizado': 'si',
                        }
                        busqueda_estudiante.write(payload_voto)

                        payload_registro = {
                            'proceso_votacion_seleccionado': procesos_votacion_rec.descripcion,
                            'candidato_seleccionado': rec_candidatos.name,
                            'votos': voto,
                            'proceso_votacion_seleccionado_objeto': procesos_votacion_rec.id,
                            'foto_candidato': foto_candidato
                        }

                        #ya hay una votacion creada con este proceso de votacion
                        # (esto me trae entonces una lista de id con todos los registros que tienen esa mismo proceso de votacion)
                        if busqueda_proceso_votacion:

                            #dentro del proceso de votacion debo buscar cada candidato, y verificar si existe con el que se está ingresando
                            for busqueda_candidato in busqueda_proceso_votacion:
                                candidato_existente = busqueda_candidato.candidato_seleccionado
                                #aqui valido si el candidato que busco ya existe o es igual que estoy intentando guardar
                                #si es asi entonces actualizo
                                if candidato_existente == rec_candidatos.name:
                                    bandera = True
                                    valor_del_voto = busqueda_candidato.votos
                                    valor_del_voto = int(valor_del_voto) + voto

                                    payload_registro['votos'] = valor_del_voto
                                    busqueda_candidato.write(payload_registro)

                                    return http.request.render('ges_votaciones.voto_exitoso', {})

                            if not bandera:
                                request.env['registro.votos'].sudo().create(payload_registro)
                                #si no existe entonces crea el candidato
                                return http.request.render('ges_votaciones.voto_exitoso', {})

                        #no hay nadie que haya votado por este proceso de votacion:
                        else:
                            request.env['registro.votos'].sudo().create(payload_registro)
                            #crea el nuevo proceso de votacion con el candidato
                            return http.request.render('ges_votaciones.voto_exitoso', {})
                    else:
                        return http.request.render('ges_votaciones.estudiante_ha_votado', {})

                #print("sigo buscando el id...")
        elif estado_proceso == 'cerrada':
            return http.request.render('ges_votaciones.proceso_votación_cerrado', {})
        else:
            return http.request.render('ges_votaciones.proceso_votación_en_borrador', {})

        response = request.render('ges_votaciones.voto_no_exitoso', {})
        return response

