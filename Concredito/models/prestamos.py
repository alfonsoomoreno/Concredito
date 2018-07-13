# -*- coding: utf-8 -*-
# Copyright 2018 Alfonso Moreno
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError


class Prestamos(models.Model):
    #Objeto que se da de alta para el manejo de las solicitudes
    _name = 'solicitudes'

    """
    Estas dos funciones siguientes son funciones especiales el cual regresan un valor para campos calculados en la vista del objeto
    solicitudes los campos calculados son los siguientes
    @interes = campo que recibe el valor de los interes a subir al prestamo
    @monto_total_pagar = campo que recibe el monto total incluyendo intereses
    Funciones que calculan los campos anteriores
    @_compute_total_interes = Funcion que calcula el valor del campo Interes
    @_compute_monto_total = Funcion que calcula el valor del campo monto_total_pagar
    Dichas funciones reciben como decoradores dos API'S las cuales son decoradores propios del ORM de odoo para el manejo de campos calculados
    o bien tambien se pueden utilizar para decorar funciones donde se aplica la logica del modulo
    Decoradores utilizados
    @api.multi = Decorador que tiene como funcion decirle a la funcion o metodo que los parametros que se mandaron se englobara en la variable
    self en este caso self es un conjunto de recordset la cual recibira como por ejemplo
    todos los campos del objeto en el cual se esta trabajando en el momento.
    @api.one = Decorador que tiene como funcion recibir solo un recordset a la vez y retornar un valor
    @api.depends = Decorador que tiene como funcion dependiendo de las variables que se le mande como parametro al decorador el campo
    calculado cambiara de forma inmediata y de forma automatica
    @api.model = Decorador que tiene como funcion simplemente instanciar una clase que ya existe en el core de odoo
    """
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

    #Columnas que contendra la tabla solicitudes
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
        'Fecha de creacion',
        default = fields.Date.today(),
    )
    date_due = fields.Date('Fecha de vigencia', default= fields.Date.today())
    monto_total_pagar = fields.Float(compute=_compute_monto_total,string='Monto total a pagar', type='float', readonly=True, store=True)

    #Funcion existente en el core que crea folio al momento de dar crear al documento se usa la clausula
    #Super el cual sirve para realizar una forma de recursividad en el sistema
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'solicitud.credito')
        return super(Prestamos, self).create(vals)

    #Funcion que simplemente actualiza el documento al estado borrador se utiliza el metodo write() propio del ORM de odoo
    @api.multi
    def action_draft(self):
        self.write({'state': 'borrador'})
        return True
    #Funcio que actualiza el estado del documento a estado cancelado
    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancelado'})
        return True
    #Funcion que evita el borrado de solicitudes confirmadas
    @api.multi
    def unlink(self):
        for c in self:
            if c.state not in ('borrador','cancelado'):
                raise UserError(
                    _("No puedes borrar una solicitud confirmada"))
        return super(Prestamos, self).unlink()
    @api.multi
    def generar_pagos(self):
        """
            Metodo extra que realize para calcular el pago mensual que el cliente pagara
            @obj_lista_pagos = Instancia del objeto de lista.pagos
            @prestamo = Variable que se le asigna el monto del prestamo al clientes
            @plazo = Variable que se le asigna el plazo de pagos que se le dara al cliente
        """
        obj_lista_pagos = self.env['lista.pagos']
        prestamo = self.prestamo
        plazo = self.plazo
        #Logica que realiza el borrado de pagos si se modifica la solicitud y se necesita volver a generar el pago
        if self.lista_pagos:
            for x in self.lista_pagos:
                query = ("""delete from lista_pagos where id = '%s'"""%(x.id))
                self.env.cr.execute(query)
        #Logica que calculo el monto de pago mensualmente incluyendo el interes en la mensualidad
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
        #Se crea el registro en la tabla de lista.pagos
        obj_lista_pagos.create({
                'pago': monto_mensualidad,
                'interes': calculo_interes,
                'total_pagar':mensualidad,
                'pagos': self.id
            }
        )
        #Se actualiza el estado a activa
        self.state = 'activa'

class ListaPagos(models.Model):
    #Objeto que se da de alta para el manejo de la lista de pagos
    _name="lista.pagos"
    #Columnas que contendra el objeto lista.pagos
    pagos = fields.Many2one(
            comodel_name='solicitudes', string='Solicitud',
            ondelete='cascade', required=True,
        )
    pago = fields.Integer('Mensualidad')
    interes = fields.Float('Monto de Interes')
    total_pagar = fields.Float('Total a pagar Mensualmente')

