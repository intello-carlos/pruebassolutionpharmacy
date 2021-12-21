from odoo import fields, models, api
from lxml import etree


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    check_status = fields.Boolean('I.', default=False)


class Picking(models.Model):
    _inherit = "stock.picking"

    check_status = fields.Boolean('I.', related='picking_type_id.check_status')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(Picking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='picking_type_id']"):
            if check_status:
                node.set('domain',
                         "[('check_status', '=', True)]")
            else:
                node.set('domain',
                         "[]")

        res['arch'] = etree.tostring(doc)

        return res