from odoo import fields, models, api
import csv
import pandas as pd
import os

from odoo.modules.module import (
    get_module_resource,
    get_resource_path
)

class ImportWizard(models.TransientModel):
    _name = 'votacion.import.wizard'
    _description = 'Importar Votaciones'

    archivo = fields.Binary(string='Archivo')

    # creo una funcion para poder leer y crear los registros de un archivo csv
    def importar_votaciones_csv(self):
        attachment = self.env['ir.attachment'].create({
            'name': 'import_file.csv',
            'datas': self.archivo,
        })
        file_path = attachment._full_path(attachment.store_fname)

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:

                descripcion = row['descripcion']
                fecha_inicio = row['fecha_inicio']
                fecha_fin = row['fecha_fin']

                votacion = self.env['proceso.votaciones'].create({
                    'descripcion': descripcion,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'estado': 'borrador'
                })

        return {'type': 'ir.actions.act_window_close'}

    # creo una funcion para poder leer y crear los registros de un archivo excel
    def importar_votaciones_excel(self):
        attachment = self.env['ir.attachment'].create({
            'name': 'import_file.xlsx',
            'datas': self.archivo,
        })
        file_path = attachment._full_path(attachment.store_fname)

        # aqui leo el archivo Excel con la libreria pandas
        df = pd.read_excel(file_path)

        # itero sobre las filas del DataFrame
        for index, row in df.iterrows():
            # Obtengo los valores de las columnas del archivo excel
            nombre_sede = row['Nombre_sede']
            descripcion = row['Descripcion']
            fecha_inicio = row['Fecha_inicio']
            fecha_fin = row['Fecha_fin']

            # creo la votación en el modelo proceso.votaciones
            self.env['proceso.votaciones'].create({
                'sede_estudio_del_estudiante': nombre_sede,
                'descripcion': descripcion,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'estado': 'borrador'
            })
        return {'type': 'ir.actions.act_window_close'}

    # funcion que me permite descargar la plantilla almacenada en el modulo
    def action_download_archivo(self):

        module_path = get_module_resource('ges_votaciones','static/document/Plantilla_Proceso_de_Votación.xlsx')
        #print("module path: ", module_path)

        # descargar el archivo desde la ubicación actual del módulo
        file_data = open(module_path, 'rb').read()

        module_path_2 = get_module_resource('ges_votaciones','static','download')

        file_name = 'plantilla_ejemplo.xlsx'  # nombre del archivo descargado

        # guardar el archivo en la ubicación deseada
        with open(os.path.join(module_path_2, file_name), 'wb') as f:
            f.write(file_data)

        return {'type': 'ir.actions.act_window_close'}
