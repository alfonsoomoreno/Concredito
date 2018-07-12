# -*- coding: utf-8 -*-
# Copyright 2018 Alfonso Moreno
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class Prestamos(models.Model):

    _name = 'solicitudes'

    @api.one
    @api.depends('plazo')
    def _compute_total_interes(self):
        if self.plazo == 3:
            self.interes = 5.0
        elif self.plazo == 6:
            self.interes = 7.0
        elif self.plazo == 9:
            self.interes = 12.0

    @api.one
    @api.depends('prestamo','interes')
    def _compute_monto_total(self):
        self.monto_total_pagar = ((self.interes / 100) * self.prestamo) + self.prestamo

    name = fields.Char(
        string='Solicitud', required=True, select=True, default="/"
    )
    nombre = fields.Many2one('res.partner','Nombre Solicitante')
    prestamo = fields.Float()
    solicitudes = fields.Char('Solicitud')
    plazo = fields.Selection(
            [(3, '3 Meses'),
             (6, '6 Meses'),
             (9, '9 Meses')], required = True)
    state = fields.Selection(
        [('borrador', 'Borrador'),
         ('activa', 'Activa'),
         ('cancelado', 'Cancelado')], string='Status', readonly=True,
        default='borrador',
    )
    lista_pagos = fields.One2many(
        comodel_name='lista.pagos', ondelete="cascade",
        inverse_name='pagos', string='Pagos',
        readonly=True,
    )

    interes = fields.Float(
        compute=_compute_total_interes, string='Tasa de interes', readonly=True,store=True,
    )

    date = fields.Date(
        'Fecha',
        default = fields.Date.today(),
    )
    monto_total_pagar = fields.Float(compute=_compute_monto_total,string='Monto total a pagar', type='float', readonly=True, store=True)
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'solicitud.credito')
        return super(Prestamos, self).create(vals)

    @api.multi
    def action_draft(self):
        self.write({'state': 'borrador'})
        return True
    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancelado'})
        return True
    @api.multi
    def unlink(self):
        for c in self:
            if c.state not in ('borrador','cancelado'):
                raise UserError(
                    _("No puedes borrar una solicitud confirmada"))
        return super(Prestamos, self).unlink()
    @api.multi
    def generar_pagos(self):
        obj_lista_pagos = self.env['lista.pagos']
        prestamo = self.prestamo
        plazo = self.plazo
        if self.lista_pagos:
            for x in self.lista_pagos:
                query = ("""delete from lista_pagos where id = '%s'"""%(x.id))
                self.env.cr.execute(query)
        if plazo == 3:
            monto_mensualidad = prestamo / plazo
            calculo_interes = ((prestamo / plazo) * (self.interes / 100))
            mensualidad = monto_mensualidad + calculo_interes
        elif plazo == 6:
            monto_mensualidad = prestamo / plazo
            calculo_interes = ((prestamo / plazo) * (self.interes / 100))
            mensualidad = monto_mensualidad + calculo_interes
        elif plazo == 9:
            monto_mensualidad = prestamo / plazo
            calculo_interes = ((prestamo / plazo) * (self.interes / 100))
            mensualidad = monto_mensualidad + calculo_interes
        obj_lista_pagos.create({
                'pago': monto_mensualidad,
                'interes': calculo_interes,
                'total_pagar':mensualidad,
                'pagos': self.id
            }
        )
        self.state = 'activa'

    class ListaPagos(models.Model):

        _name="lista.pagos"

        pagos = fields.Many2one(
                comodel_name='solicitudes', string='Cost distribution',
                ondelete='cascade', required=True,
            )
        pago = fields.Integer('Mensualidad')
        interes = fields.Float('Monto de Interes')
        total_pagar = fields.Float('Total a pagar Mensualmente')

