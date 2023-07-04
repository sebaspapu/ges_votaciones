# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class ProcesoVotacionSitioWeb(http.Controller):

    #creo una ruta para ingresar a la pestaña de identificacion, posterior a esto se redirecciona a el formulario de identificacion
    @http.route('/menu_identificacion', type="http", auth="public", website=True)
    def menu_identificacion_estudiante(self, **kwargs):
        print("Ingreso al menu de identificacion de estudiante!!!")
        return http.request.render('ges_votaciones.form_identificarse', {})

    #valido si el estudiante existe o no, tambien valido si el estudiante ya votó
    @http.route('/validacion/valido_identificacion', type="http", auth="public", website=True)
    def validacion_identificacion(self, **kwargs):

        numero_ident = int(kwargs.get('vat'))
        print("Aqui valido si el estudiante existe!!! Argumentos: ", kwargs, numero_ident , type(numero_ident))

        #ahora si vamos a buscar al contacto dentro del modelo de res.partner
        busqueda = request.env['res.partner'].sudo().search([('tipo_persona','=','estudiante')])
        print("busqueda: ", busqueda)

        plantilla_record = 'ges_votaciones.no_hay_estudiante_de_ese_tipo'

        if busqueda:
            for rec in busqueda:
                nume_iden_res = int(rec.vat)
                print(f"id contacto: {rec.id} validar si el numero de identificacion del estudiante existe!",
                      nume_iden_res, type(nume_iden_res))

                #buscar si el estudiante ya ha participado en un proceso de votacion
                estado_su_voto = rec.voto_realizado
                print("estado del voto: ", estado_su_voto, type(estado_su_voto))

                plantilla_record = 'ges_votaciones.estudiante_no_existente'

                if (numero_ident == nume_iden_res):
                    print("El numero de identificacion existe")

                    if estado_su_voto == 'no':
                        print("El estudiante aún no ha votado")

                        #le envio el modelo que contiene todos los procesos de votacion
                        procesos_votacion_rec = request.env['proceso.votaciones'].sudo().search([])
                        print("Objeto con id de todos los procesos de votacion: ", procesos_votacion_rec)

                        #le envio el modelo que contiene todos los candidatos disponibles
                        candidatos_disponibles_rec = request.env['res.partner'].sudo().search([('tipo_persona','=','candidato')])
                        print("Objeto con id de todos los candidatos: ",candidatos_disponibles_rec)

                        if procesos_votacion_rec:
                            if candidatos_disponibles_rec:

                                # le muestro un mensaje de que el estudiante se encuentra: (luego cambiara)
                                return http.request.render('ges_votaciones.form_votacion', {
                                    'busqueda_num_id_rec':rec,
                                    'procesos_votacion_rec': procesos_votacion_rec,
                                    'candidatos_disponibles_rec': candidatos_disponibles_rec,
                                    })
                            else:
                                plantilla_record = 'ges_votaciones.no_hay_candidatos_disponibles'
                                break
                        else:
                            plantilla_record = 'ges_votaciones.no_hay_procesos_de_votacion'
                            break
                    else:
                        plantilla_record = 'ges_votaciones.estudiante_ha_votado'
                        break
                else:
                    plantilla_record = 'ges_votaciones.estudiante_no_existente'

                print("sigue buscando ...")
            print("El numero de identificacion NO existe")
        print("No existe un contacto de tipo estudiante aún")
        return http.request.render(plantilla_record, {})

    #pagina en donde se encuentra mi formulario para poder realizar el proceso de votación
    @http.route('/votacion/formulario', type="http", auth="public", website=True)
    def proceso_votacion(self, **kwargs):
        print("Ingreso al formulario de votación!!!", kwargs)
        id_votacion_seleccionada = int(kwargs.get('id_votacion_seleccionada'))
        id_candidato_seleccionado = int(kwargs.get('id_candidato_seleccionado'))
        id_estudiante_votante = int(kwargs.get('busqueda_num_id_rec'))
        #primero realizo la validacion para saber si el candidato existe dentro de ese Proceso de votacion seleccionado
        procesos_votacion_rec = request.env['proceso.votaciones'].sudo().search([('id','=',id_votacion_seleccionada)])

        #busqueda estudiante
        busqueda_estudiante = request.env['res.partner'].sudo().search([('id', '=',id_estudiante_votante)])

        # buscar si el estudiante ya ha participado en un proceso de votacion
        estado_su_voto = busqueda_estudiante.voto_realizado
        print("estado del voto: ", estado_su_voto, type(estado_su_voto))

        print("proceso de votacion: ", procesos_votacion_rec)

        cantidad_candidatos = procesos_votacion_rec.candidatos

        for rec_candidatos in cantidad_candidatos:
            print("id candidatos: ", rec_candidatos)
            if int(rec_candidatos.id) == id_candidato_seleccionado:
                print("El candidato existe!\nredirigiendo...")

                #creemos el registro en el modelo: (Almaceno los objetos que contienen toda la informacion)
                print("Almaceno el 'Objeto-id' del proceso de votacion: ", procesos_votacion_rec)
                print("Almaceno el 'Objeto-id' del candidato seleccionado: ", rec_candidatos)

                #busco el proceso de seleccion para ver si ya existe, y no volver a crear un mismo proceso
                busqueda_proceso_votacion = request.env['registro.votos'].sudo().search([
                    ('proceso_votacion_seleccionado','=',procesos_votacion_rec.descripcion)])
                print("busqueda_proceso_votacion: ", busqueda_proceso_votacion)

                bandera = False
                voto = 1
                foto_candidato = rec_candidatos.image_1920

                if estado_su_voto == 'no':
                    print("El estudiante aún no ha votado")

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
                            print(f"id candidato que existe dentro de el proceso de votacion {busqueda_candidato.id}: ", candidato_existente)
                            print(f"id candidato que estoy ingresando dentro de el proceso de votacion {busqueda_candidato.id}: ", rec_candidatos.name)
                            #aqui valido si el candidato que busco ya existe o es igual que estoy intentando guardar
                            #si es asi entonces actualizo
                            if candidato_existente == rec_candidatos.name:
                                bandera = True
                                valor_del_voto = busqueda_candidato.votos
                                print("de cuanto es el valor del voto: ", valor_del_voto)
                                valor_del_voto = int(valor_del_voto) + voto
                                print("actualiza el valor del voto actualizado: ", valor_del_voto)

                                payload_registro['votos'] = valor_del_voto
                                busqueda_candidato.write(payload_registro)

                                print("esto quiere decir que el candidato existe, actualiza el valor del voto, en este caso aumenta el valor del voto!!")
                                return http.request.render('ges_votaciones.voto_exitoso', {})

                        if not bandera:
                            request.env['registro.votos'].sudo().create(payload_registro)
                            #si no existe entonces crea el candidato
                            print("esto quiere decir que el candidato NO existe, lo crea y registra el valor del voto en 1!!")
                            return http.request.render('ges_votaciones.voto_exitoso', {})

                    #no hay nadie que haya votado por este proceso de votacion:
                    else:
                        request.env['registro.votos'].sudo().create(payload_registro)
                        #crea el nuevo proceso de votacion con el candidato
                        print("esto quiere decir que no hay un proceso de votacion, asi que lo crea , y lo crea con un solo voto , osea voto=1 !!!")
                        return http.request.render('ges_votaciones.voto_exitoso', {})
                else:
                    print("el estudiante ya votó")
                    return http.request.render('ges_votaciones.estudiante_ha_votado', {})

            print("sigo buscando el id...")

            #luego aqui valido si ese id del candidato que acaba de encontrar es igual al id que selecciono en el formulario
            #si son iguales entonces puede registrar el voto, si no es igual entonces no podra votar, y debe seguir buscando
        print("El candidato no existe!")
        #flash("El candidato no existe. Por favor, selecciona otro candidato.", "error")
        #return http.request.render('ges_votaciones.form_votacion', {})
        #values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        #values['error'] = _("Wrong")
        response = request.render('ges_votaciones.voto_no_exitoso', {})
        return response

