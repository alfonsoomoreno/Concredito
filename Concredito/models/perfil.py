# -*- coding: utf-8 -*-
# Copyright 2018 Alfonso Moreno
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

#Librerias necesarias a importar para usarse en la clase
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from datetime import datetime

class HistorialCrediticio(models.Model):
    """
    @_name = Forma que se da de alta un nuevo objeto o tabla dentro del sistema
    Se dan de alta las columna que contendra el objeto perfil asignado al parametro @_name
    """
    _name = 'perfil'
    #Columnas que contendra el objeto perfil
    partner_id = fields.Many2one('res.partner','Nombre del Cliente')

    solicitudes_pendientes= fields.One2many(
        comodel_name='solicitudes.pendientes', ondelete="cascade",
        inverse_name='solicitudes', string='Solicitudes pendientes',
        readonly=True,
    )
    @api.multi
    def SolicitudesPendientes(self):
        """
        Metodo que te regresa las solicitudes pendientes del cliente seleccionado en la vista
        Variables que se utilizan
        @obj_historial_sol = Instancia del objeto solicitudes
        @pbj_solicitudes_pendientes = Instacia del objeto solicitudes.pendientes
        @perfiles = Arreglo que se utiliza para llenar dependiendo si hay registros en el campo solicitudes_pendientes
        @registros = Recordset de los valores encontrados por el metodo serach() propio del ORM
        @ORM = Framework de odoo
        """
        obj_historial_sol = self.env['solicitudes']
        obj_solicitudes_pendientes = self.env['solicitudes.pendientes']
        """Dominio creado para buscar por medio del ORM de odoo con la funcion especial search() el cual es mucho mas rapido que un query"""
        dominio = [('nombre','=', self.partner_id.id),
                   ('state','in',['borrador'])]
        perfiles = []
        registros = obj_historial_sol.search(dominio)
        """Como la variable @solicitudes_pendientes es una relacion One2many en el framework de odoo se puede recorrer por medio
           de un for los valores que tiene asignados y asi agregar los ids existentes en el arreglo perfiles
        """
        for reg in self.solicitudes_pendientes:
            perfiles.append(reg.name_sol.id)
        #Validacion para combrobar si viene vacia la variable registros si es asi lanza un Mensaje de error al usuario
        if registros:
            for reg in registros:
                if reg.id not in perfiles:
                    #Se convierte de @str a @date para poder sacar la diferencia en las fechas
                    fecha_inicial = datetime.strptime(reg.date, '%Y-%m-%d')
                    fecha_final = datetime.strptime(reg.date_due, '%Y-%m-%d')
                    fecha = fecha_inicial - fecha_final
                    #se crea el diccionario para mandar como parametro al metodo create()
                    solicitudes = {
                                'name_sol': reg.id,
                                'solicitud': reg.solicitudes,
                                'prestamo': reg.prestamo,
                                'estado': reg.state,
                                'vigencia': abs(fecha.days),
                                'solicitudes': self.id
                                }
                    #Funcion propia del ORM para crear registros dentro de las tablas del sistema
                    obj_solicitudes_pendientes.create(solicitudes)
        else:
            #Mensaje de error que lanza si el sistema no encontro ningun registros en el search()
            raise UserError("El cliente seleccionado no tiene solicitudes de creditos pendientes")

class historialsolicitudes(models.Model):
    """Se crea el objeto o tabla solicitudes_pendientes en el sistema con sus respectivas columnas"""
    _name = 'solicitudes.pendientes'

    #Columnas que contendra el objeto solicitudes.pendientes
    solicitudes = fields.Many2one(
            comodel_name='perfil', string='Solicitudes pendientes',
            ondelete='cascade', required=True,
        )
    name_sol = fields.Many2one('solicitudes','Solicitud')
    solicitud = fields.Char('Concepto del prestamo')
    prestamo = fields.Integer('Monto del prestamo')
    estado = fields.Char('Estado')
    vigencia = fields.Integer('Dias de vigencia')

