# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class Quotator(models.Model):
    _name = "quotator.own"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Solution Pharmacy Quotator"
    _order = "sequence, id"
    _check_company_auto = True

    name = fields.Char('Reference', copy=False, default=lambda self: _('New'), required=True)
    final_product = fields.Char(string="Final product", required=True)
    product_qty = fields.Integer(string="Quantity", default=1.0, readonly="True")
    sequence = fields.Integer('Sequence')
    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    user = fields.Many2one('res.users', string='Quotator', required=True, readonly=True, default=lambda self: self.env.user)
    quotator_date = fields.Date(string="Quotation date", readonly=True, index=True, default=fields.Date.context_today)
    expiration_date = fields.Date(string="Expiration date", required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.company)
    patient = fields.Char(string="Patient")
    pharmaceutical_form = fields.Many2one('pharmaceutical.form', string="Pharmaceutical form", required=True)
    quotator_lines = fields.One2many('quotator.lines', 'quotator_id', string="Materials")
    subtotal_grams = fields.Integer(string="subtotal size(gr)", required=True, default=1.0)
    total_grams = fields.Integer(string="Total size(gr)", compute="_compute_size_total", store=True)
    value_pharmaceutical_form = fields.Float(string="size(g) pharmaceutical form", compute="_compute_subtotal_pharmaceutical", store=True)
    total_pharmaceutical_form = fields.Float(string="Total", compute="_compute_total_pharmaceutical", store=True)
    total = fields.Float(string="Total", compute="_compute_total_quotator")
    medical_formula = fields.Binary('Medical formula', required=True)
    presentation_id = fields.Many2one('pharmaceutical.presentation', string='Farmaceutical presentation')
    line_production_id = fields.Many2one('production.lines', string="Production Lines")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('quotator.own') or _('New')
        return super(Quotator, self).create(vals)
    
    @api.depends('subtotal_grams', 'product_qty')
    def _compute_size_total(self):
        for line in self:
            line['total_grams'] = line['product_qty'] * line['subtotal_grams']

    @api.depends('value_pharmaceutical_form', 'pharmaceutical_form')
    def _compute_total_pharmaceutical(self):
        for line in self:
            line['total_pharmaceutical_form'] = line['value_pharmaceutical_form'] * line.pharmaceutical_form.value
##Revisar##
    @api.depends('quotator_lines')
    def _compute_subtotal_pharmaceutical(self):
        suma = 0.0
        for line in self.quotator_lines:
            suma += line['material_qty']
        if suma > self.total_grams: 
            raise ValidationError(_('The percentages are not correct'))   
        else:
            self.value_pharmaceutical_form = (self.total_grams - suma)
    
    @api.onchange('quotator_lines', 'subtotal_grams')
    def _clean_raw_materia(self):
        if self.partner_id.client_type.name in ('Especialista', 'Distribuidor', 'Paciente', 'Empleado'):
            if self.subtotal_grams <= 0 or self.subtotal_grams > 1000:
                self.quotator_lines = False
                return {
                    'warning':{
                        'title': "Valores incorrectos",
                        'message': "La cantidad de gramos por producto no es correcta, cámbiela",
                    },
                }

    @api.depends('quotator_lines.price_total', 'total_pharmaceutical_form')
    def _compute_total_quotator(self):
        suma = 0.0
        for record in self.quotator_lines:
            suma += record.price_total

        percentages = self.env['discount.rates'].search([('type_id.id', "=", self.partner_id.client_type.id)])
        presentation = self.presentation_id.value+((self.presentation_id.value*percentages['percentage'])/100)
        pharmaceutical = self.total_pharmaceutical_form+((self.total_pharmaceutical_form*percentages['percentage'])/100)
        total = suma+presentation+pharmaceutical
        for line in percentages.lines_price:
            if self.subtotal_grams in range(line['start'], line['final']+1):
                if total < line['base_price']:
                    total = line['base_price']
                else:
                    total = total
        self.total = total

    @api.constrains('quotator_date')
    def _validation_date(self):
        if self.expiration_date < self.quotator_date:
            raise ValidationError(_("The expiration date cannot be less than the application creation date"))
    
    @api.constrains('quotator_lines')
    def _validar_raw_material(self):
        if not self.quotator_lines:
            raise UserError(_("There are no selected raw materials"))

    def send_quotation(self):
        material = []
        products = []
        product = {
            'product_id': self.env['product.template'].search([('name', '=', 'Generico cotizador')]).id,
            'name': self.final_product,
            'pharmaceutical_form': self.pharmaceutical_form.id,
            'product_uom_qty': self.product_qty,
            'price_unit': self.total/self.product_qty,
            'price_subtotal': self.total,
            'grams_pharmaceutical': self.value_pharmaceutical_form,
        }
        products.append((0,0,product))
        for line in self.quotator_lines:
            raw = {
                'product_id': line.product_id.id,
                'product_qty': line.material_qty,
                'percentage': line.percentage,
                'price_unit': 0,
                'appointment_id': line.quotator_id.id,
                'category': line.category,
                'sale_order': line.sale_order,
            }
            material.append((0,0,raw))
        vals = {
                'user_id' : self.user.id,
                'partner_id': self.partner_id.id,
                'date_order': self.quotator_date,
                'validity_date': self.expiration_date,
                'pricelist_id': self.partner_id.property_product_pricelist,
                'order_line': products,
                'raw_material': material,
                'medical_formula': self.medical_formula,
                'production_line_id': self.line_production_id.id,
                'final_client': self.patient,
            }
        self.env['sale.order'].create(vals)
        self.state = 'posted'
    
    def action_cancel(self):
        self.state = 'cancel'