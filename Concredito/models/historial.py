# -*- coding: utf-8 -*-
# Copyright 2018 Alfonso Moreno
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models,_
from openerp.exceptions import Warning as UserError

class HistorialCrediticio(models.Model):
    #Objeto que se da de alta para el manejo del historial crediticio
    _name = 'historial.crediticio'
    #Columnas que contendran el objeto historial.crediticio
    partner_id = fields.Many2one('res.partner','Nombre del Cliente')

    historial = fields.One2many(
        comodel_name='historial.solicitudes', ondelete="cascade",
        inverse_name='solicitudes', string='Pagos',
        readonly=True,
    )
    @api.multi
    def ImportarSolicitudes(self):
        """
        Metodo que importa las solicitudes de la tabla @solicitudes y las cual las inserta en la tabla @historial_solicitudes
        para el historial del cliente y asi el usuario poder dirigirse directamente a la solicitud
        @obj_historial_sol = Instancia del objeto historial_solicitudes
        @query = Variable que contiene la cadena completa del query a ejecutar para consultar informacion en la base de datos
        @registros = Variable que cacha todos los registros obtenidos en la consulta a la base de datos
        @historial = Arreglo que se llena de forma automatica cuando el sistema encuentra registros en el campo historial
        """
        obj_historial_sol = self.env['historial.solicitudes']
        query = ("""select id,solicitudes,prestamo,state from solicitudes where nombre = %s"""%(self.partner_id.id))
        self.env.cr.execute(query)
        registros = self.env.cr.fetchall()
        historial = []

        #Se itera el campo historial ya que es un campo con la relacion One2many y se inserta los varoles obtenidos en la iteracion
        #al arreglo historial
        for reg in self.historial:
            historial.append(reg.name_sol.id)
        #Si no vienen registros el sistema lanza un mensaje de error
        if registros:
            for reg in registros:
                if reg[0] not in historial:
                    #Se crea el diccionario el cual se manda como parametro al metodo create() propio del ORM
                    solicitudes = {
                        'name_sol': reg[0],
                        'solicitud': reg[1],
                        'prestamo': reg[2],
                        'estado': reg[3],
                        'solicitudes': self.id
                        }
                    #Se crea el registro en la tabla historial_solicitudes
                    obj_historial_sol.create(solicitudes)
        else:
            #Mensaje de error cuando el sistema detecta que viene vacia la variable registros
            raise UserError(
                    _("Este cliente no tiene solicitudes creadas, Favor de crear una nueva solicitud"))

class historialsolicitudes(models.Model):
    #Objeto que se da de alta para el manejo del historial solicitudes
    _name = 'historial.solicitudes'

    #Columnas que contendran el objeto historial.solicitudes
    solicitudes = fields.Many2one(
            comodel_name='historial.crediticio', string='Historial de credito',
            ondelete='cascade', required=True,
        )
    name_sol = fields.Many2one('solicitudes','Solicitud')
    solicitud = fields.Char('Concepto del prestamo')
    prestamo = fields.Integer('Monto del prestamo')
    estado = fields.Char('Estado')
