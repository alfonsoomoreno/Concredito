# -*- coding: utf-8 -*-
# Copyright 2018 Alfonso Moreno
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#Librerias usadas en la clase
from openerp import api, fields, models

class NuevaSolicitud(models.TransientModel):
    """Objeto que se da de alta en el sistema"""
    _name = 'nueva.solicitud'
    #Columnas que contendra el objeto nueva.solicitud
    solicitud = fields.Char('Solicitud')

    prestamo = fields.Float()

    plazo = fields.Selection(
            [(3, '3 Meses'),
             (6, '6 Meses'),
             (9, '9 Meses')], required = True)

    @api.multi
    def NuevaSolicitud(self):
        """
        Metodo que te lanza un pequeño wizard para dar de alta nuevas solicitudes para el cliente seleccionado en la vista
        @nueva_solicitud = Diccionario que se utiliza para mandar como parametro al metodo create propio del ORM de odoo
        @create() = metodo propio del ORM que da de alta registros en un objeto en especifico
        @active_id = saco el id activo del registro donde se encuentra ejecuntando el wizard
        """
        obj_solicitudes = self.env['solicitudes']
        #Saco id activo del registro actual donde se encuentra el wizard
        active_id = self.env['historial.crediticio'].browse(
            self.env.context['active_id'])
        #Diccionario para crear una nueva solicitud en el objeto solicitudes
        nueva_solicitud = {
                'nombre': active_id.partner_id.id,
                'solicitudes': self.solicitud,
                'prestamo': self.prestamo,
                'plazo': self.plazo
            }
        #Se crea el registro en la tabla solicitudes
        obj_solicitudes.create(nueva_solicitud)