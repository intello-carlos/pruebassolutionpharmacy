from lxml import etree
from odoo import fields, models, api, exceptions, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _default_production_line(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        if check_status:
            return self.env['production.lines'].search([('check_status', '=', check_status)], limit=1)
        else:
            return False

    production_line_id = fields.Many2one('production.lines', string='Production line', default=_default_production_line)
    check_status = fields.Boolean('I.', store=True) #,compute='_check_status'
    dough = fields.Many2one("uom.uom", readonly=True)
    size = fields.Float(string="Size")
    size_total = fields.Float(string="Size total", compute="_size_total")
    percent_total = fields.Float(compute="_percent_total", store=True, digits=(12, 4))
    status_percent = fields.Selection([("0", "Total percentage is below 100"),
                                       ("1", "The total percentage is the ideal")], store=True)
    standard_manufacturing = fields.Boolean(related="product_tmpl_id.standard_manufacturing", store=True)
    pharmaceutical_form = fields.Many2one('pharmaceutical.form',
                                          string="Pharmaceutical form")
    pharmaceutical_presentation = fields.Many2one('pharmaceutical.presentation',
                                                  string="Pharmaceutical presentation")
    @api.onchange('product_tmpl_id')
    def _onchange_product_id(self):
        self.pharmaceutical_form = False
        self.pharmaceutical_presentation = False
        if self.product_tmpl_id:
            self.pharmaceutical_form = self.product_tmpl_id.pharmaceutical_form
            self.pharmaceutical_presentation = self.product_tmpl_id.pharmaceutical_presentation 

    @api.onchange('production_line_id')
    def _check_status_product_tmp(self):
        if self.product_tmpl_id:
            if self.production_line_id.check_status != self.product_tmpl_id.check_status:
                self.product_tmpl_id = None

        domain = {'product_tmpl_id': [('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False),
                                      ('company_id', '=', 'company_id'),
                                      ('check_status', '=', self.production_line_id.check_status)]}
        return {'domain': domain}

    @api.onchange('production_line_id')
    def _check_status(self):
        if self.production_line_id:
            self.check_status = self.production_line_id.check_status

    @api.depends("bom_line_ids")
    def _percent_total(self):
        for mrp_bom in self:
            total_percent = 0
            # Bloque for: calcula el total de porcentajes
            for bom in mrp_bom.bom_line_ids:
                percent = bom["percent"]
                total_percent = round(total_percent + percent, 4)
            # Bloque if: Cambia el estado del porcentaje dependiendo del total
            if total_percent < 100:
                mrp_bom.status_percent = "0"
                mrp_bom.percent_total = total_percent
            else:
                if total_percent == 100:
                    mrp_bom.status_percent = "1"
                    mrp_bom.percent_total = total_percent
                else:
                    raise exceptions.ValidationError("The total percentage exceeds 100%")

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if "standard_manufacturing" in val:
                if val["standard_manufacturing"]:
                    # Bloque if: Restringir la creacion de la lista si elporcentaje se excede de 100%
                    if "percent_total" in val:
                        if val["percent_total"] == 100:
                            return super(MrpBom, self).create(val)
                        else:
                            raise exceptions.ValidationError(
                                "The product is of standard manufacture, the total percentage must be equal to 100%")
                    else:
                        return super(MrpBom, self).create(val)
                else:
                    if "percent_total" in val:
                        if val["percent_total"] <= 100:
                            return super(MrpBom, self).create(val)
                        else:
                            raise exceptions.ValidationError("The total percentage exceeds 100%")
                    else:
                        return super(MrpBom, self).create(val)
            else:
                return super(MrpBom, self).create(val)

    def write(self, vals):
        # Bloque if: Restringir la creacion de la lista si elporcentaje se excede de 100%
        if "standard_manufacturing" in vals:
            if vals["standard_manufacturing"]:
                # Bloque if: Restringir la creacion de la lista si elporcentaje se excede de 100%
                if "percent_total" in vals:
                    if vals["percent_total"] == 100:
                        return super(MrpBom, self).write(vals)
                    else:
                        raise exceptions.ValidationError(
                            "The product is of standard manufacture, the total percentage must be equal to 100%")
                else:
                    if "percent_total" in self:
                        if self.percent_total == 100:
                            return super(MrpBom, self).write(vals)
                        else:
                            raise exceptions.ValidationError(
                                "The product is of standard manufacture, the total percentage must be equal to 100%")
                    else:
                        return super(MrpBom, self).write(vals)
            else:
                if "percent_total" in vals:
                    if vals["percent_total"] <= 100:
                        return super(MrpBom, self).write(vals)
                    else:
                        raise exceptions.ValidationError("The total percentage exceeds 100%")
                else:
                    if "percent_total" in self:
                        if self.percent_total <= 100:
                            return super(MrpBom, self).write(vals)
                        else:
                            raise exceptions.ValidationError("The total percentage exceeds 100%")
                    else:
                        return super(MrpBom, self).write(vals)
        else:
            if "standard_manufacturing" in self:
                if self.standard_manufacturing:
                    # Bloque if: Restringir la creacion de la lista si elporcentaje se excede de 100%
                    if "percent_total" in vals:
                        if vals["percent_total"] == 100:
                            return super(MrpBom, self).write(vals)
                        else:
                            raise exceptions.ValidationError(
                                "The product is of standard manufacture, the total percentage must be equal to 100%")
                    else:
                        if "percent_total" in self:
                            if self.percent_total == 100:
                                return super(MrpBom, self).write(vals)
                            else:
                                raise exceptions.ValidationError(
                                    "The product is of standard manufacture, the total percentage must be equal to 100%")
                        else:
                            return super(MrpBom, self).write(vals)
                else:
                    if "percent_total" in vals:
                        if vals["percent_total"] <= 100:
                            return super(MrpBom, self).write(vals)
                        else:
                            raise exceptions.ValidationError("The total percentage exceeds 100%")
                    else:
                        if "percent_total" in self:
                            if self.percent_total <= 100:
                                return super(MrpBom, self).write(vals)
                            else:
                                raise exceptions.ValidationError("The total percentage exceeds 100%")
                        else:
                            return super(MrpBom, self).write(vals)

    @api.depends("size", "product_qty")
    def _size_total(self):
        self.size_total = self.size * self.product_qty

    @api.onchange("product_tmpl_id")
    def value_size(self):
        self.size = self.product_tmpl_id.size
        self.dough = self.product_tmpl_id.dough

    @api.onchange("size", "product_qty")
    def _compute_percent_quantity_line(self):
        if self.size and self.product_qty:
            for line in self.bom_line_ids:
                line.formula_percent()
                line.formula_product_qty()

    @api.depends("product_qty")
    def _validate_size(self):
        if self.size == 0:
            raise exceptions.UserError(_("Quantity must be greater than zero"))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(MrpBom, self).fields_view_get(view_id=view_id,
                                                  view_type=view_type,
                                                  toolbar=toolbar,
                                                  submenu=submenu)

        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='production_line_id']"):
            if check_status:
                node.set('domain', "[('check_status', '=', True)]")
            else:
                node.set('domain', "[]")

        res['arch'] = etree.tostring(doc)

        return res


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    percent = fields.Float(digits='Precision Mrp', string="Float")
    affect_bill_materials = fields.Boolean('Affects bill of materials', related='product_id.affect_bill_materials')
    check_change_terms = fields.Selection(
        selection=[('percent', 'percent'), ('product_qty', 'product qty'), ('none', 'none')], default='none')
    product_qty = fields.Float('Quantity', default=1.0, digits='Precision Mrp', required=True)

    @api.depends('product_qty')
    @api.onchange('product_id', 'percent')
    def formula_percent(self):
        # def formula_percent(self): La funcion aplica la formula para cantidad segun el porcentaje para cada componente
        for line in self:
            if line.affect_bill_materials:
                # product_size: valor total del producto

                if line.percent == 0:
                    line.product_qty = 0
                    self.check_change_terms = 'none'

                else:
                    if self.check_change_terms in ('none', 'percent'):
                        if self.check_change_terms == 'none':
                            self.check_change_terms = 'product_qty'

                            product_size_total = line.bom_id.size_total
                            percent = line.percent
                            # line.product_qty: Almacena la cantidad dependiendo del porcentaje y el valor del producto
                            line.product_qty = (product_size_total * percent) / 100

                        if self.check_change_terms == 'percent':
                            self.check_change_terms = 'none'
            else:
                line.product_qty = 0

    @api.depends('percent','product_id')
    @api.onchange('product_qty')
    def formula_product_qty(self):
        # def formula_product_qty(self): La funcion aplica la formula inversa para cada componente
        for line in self:
            if line.affect_bill_materials:

                if line.product_qty == 0:
                    line.percent = 0
                    self.check_change_terms = 'none'

                else:
                    if self.check_change_terms in ('none', 'product_qty'):
                        if self.check_change_terms == 'none':
                            self.check_change_terms = 'percent'

                            product_size_total = line.bom_id.size_total
                            product_qty = line.product_qty
                            if product_size_total != 0:
                                # line.percent: Almacena el porcentaje dependiendo de la cantidad y el valor del producto
                                line.percent = (product_qty * 100) / product_size_total

                        if self.check_change_terms == 'product_qty':
                            self.check_change_terms = 'none'
            else:
                line.percent = 0
