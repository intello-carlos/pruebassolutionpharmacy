from lxml import etree
import json
from odoo import api, fields, models, exceptions, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    check_status = fields.Boolean('I.', readonly=1, default=True)
    check_status_group = fields.Boolean('Check product group', related="product_group.check_status")
    check_status_categ = fields.Boolean('Check product categ', related="categ_id.check_status")
    pharmaceutical_form = fields.Many2one('pharmaceutical.form', string="Pharmaceutical form")
    pharmaceutical_presentation = fields.Many2one('pharmaceutical.presentation', string="Pharmaceutical presentation")
    dough = fields.Many2one("uom.uom", domain=['|', ("category_id.measure_type", "=", "weight"),
                                               ("category_id.measure_type", "=", "volume")])
    size = fields.Float(string="Size")

    """Boolean Fields"""
    standard_manufacturing = fields.Boolean("Standard manufacturing")
    affect_bill_materials = fields.Boolean('Affects bill of materials', default=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(ProductTemplate, self).fields_view_get(view_id=view_id,
                                                           view_type=view_type,
                                                           toolbar=toolbar,
                                                           submenu=submenu)

        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='product_group']"):
            if check_status:
                node.set('domain', "[('check_status', '=', True)]")
            else:
                node.set('domain', "[]")

        for node in doc.xpath("//field[@name='check_status']"):
            if check_status:
                node.set("readonly", "1")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))
            else:
                node.set("readonly", "0")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = ['|',('check_status_group', '=',False),('check_status_categ', '=',False)]
                node.set("modifiers", json.dumps(modifiers))

        res['arch'] = etree.tostring(doc)

        return res

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        self.check_status = self.categ_id.check_status

    @api.onchange('product_group')
    def onchange_product_group(self):

        domain = {'categ_id': []}
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        if self.product_group.check_status != self.categ_id.check_status:
            self.categ_id = False

        if check_status:
            domain = {'categ_id': [('check_status', '=', True)]}
        else:
            if not self.product_group.check_status:
                domain = {'categ_id': [('check_status', '=', False)]}

        return {'domain': domain}


class Product(models.Model):
    _inherit = 'product.product'

    def default_check_status(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        return check_status

    check_status = fields.Boolean('I.', default=default_check_status, related='product_tmpl_id.check_status')
    check_status_group = fields.Boolean('Check product group', related="product_group.check_status")
    check_status_categ = fields.Boolean('Check product categ', related="categ_id.check_status")
    affect_bill_materials = fields.Boolean('Affects bill of materials', related='product_tmpl_id.affect_bill_materials')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(Product, self).fields_view_get(view_id=view_id,
                                                   view_type=view_type,
                                                   toolbar=toolbar,
                                                   submenu=submenu)

        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='product_group']"):
            if check_status:
                node.set('domain', "[('check_status', '=', True)]")
            else:
                node.set('domain', "[]")

        for node in doc.xpath("//field[@name='check_status']"):
            if check_status:
                node.set("readonly", "1")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))
            else:
                node.set("readonly", "0")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = ['|',('check_status_group', '=',False),('check_status_categ', '=',False)]
                node.set("modifiers", json.dumps(modifiers))

        res['arch'] = etree.tostring(doc)

        return res

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        self.check_status = self.categ_id.check_status

    @api.onchange('product_group')
    def onchange_product_group(self):

        domain = {'categ_id': []}
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        if self.product_group.check_status != self.categ_id.check_status:
            self.categ_id = False

        if check_status:
            domain = {'categ_id': [('check_status', '=', True)]}
        else:
            if not self.product_group.check_status:
                domain = {'categ_id': [('check_status', '=', False)]}

        return {'domain': domain}


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def default_check_status(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        return check_status

    check_status = fields.Boolean('I.', default=default_check_status)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(ProductCategory, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                           submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='check_status']"):
            if check_status:
                node.set("readonly", "1")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))
            else:
                node.set("readonly", "0")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = False
                node.set("modifiers", json.dumps(modifiers))

        res['arch'] = etree.tostring(doc)

        return res


class ProductGroup(models.Model):
    _inherit = 'product.group'

    def default_check_status(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        return check_status

    check_status = fields.Boolean('I.', default=default_check_status)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(ProductGroup, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='check_status']"):
            if check_status:
                node.set("readonly", "1")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))
            else:
                node.set("readonly", "0")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = False
                node.set("modifiers", json.dumps(modifiers))

        res['arch'] = etree.tostring(doc)

        return res
