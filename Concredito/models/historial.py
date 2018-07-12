# -*- coding: utf-8 -*-
# Copyright 2018 Alfonso Moreno
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError

class HistorialCrediticio(models.Model):
    _name = 'historial.crediticio'

    partner_id = fields.Many2one('res.partner','Nombre del Cliente')

    historial = fields.One2many(
        comodel_name='historial.solicitudes', ondelete="cascade",
        inverse_name='solicitudes', string='Pagos',
        readonly=True,
    )
    @api.multi
    def ImportarSolicitudes(self):
        obj_historial_sol = self.env['historial.solicitudes']
        query = ("""select id,solicitudes,prestamo,state from solicitudes where nombre = %s"""%(self.partner_id.id))
        self.env.cr.execute(query)
        registros = self.env.cr.fetchall()
        historial = []

        for reg in self.historial:
            historial.append(reg.name_sol.id)
        if registros:
            for reg in registros:
                if reg[0] not in historial:
                    solicitudes = {
                        'name_sol': reg[0],
                        'solicitud': reg[1],
                        'prestamo': reg[2],
                        'estado': reg[3],
                        'solicitudes': self.id
                        }
                    obj_historial_sol.create(solicitudes)
        else:
            raise UserError(
                    _("Este cliente no tiene solicitudes creadas, Favor de crear una nueva solicitud"))

    class historialsolicitudes(models.Model):
        _name = 'historial.solicitudes'

        solicitudes = fields.Many2one(
                comodel_name='historial.crediticio', string='Historial de credito',
                ondelete='cascade', required=True,
            )
        name_sol = fields.Many2one('solicitudes','Solicitud')
        solicitud = fields.Char('Concepto del prestamo')
        prestamo = fields.Integer('Monto del prestamo')
        estado = fields.Char('Estado')
