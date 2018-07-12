# -*- coding: utf-8 -*-
# Copyright 2018 Alfonso Moreno
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError

class NuevaSolicitud(models.TransientModel):
    _name = 'nueva.solicitud'

    solicitud = fields.Char('Solicitud')

    prestamo = fields.Float()

    plazo = fields.Selection(
            [(3, '3 Meses'),
             (6, '6 Meses'),
             (9, '9 Meses')], required = True)

    @api.multi
    def NuevaSolicitud(self):
        obj_solicitudes = self.env['solicitudes']
        active_id = self.env['historial.crediticio'].browse(
            self.env.context['active_id'])
        nueva_solicitud = {
                'nombre': active_id.partner_id.id,
                'solicitudes': self.solicitud,
                'prestamo': self.prestamo,
                'plazo': self.plazo
            }
        obj_solicitudes.create(nueva_solicitud)