from lxml import etree
from odoo import api, fields, models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(MrpUnbuild, self).fields_view_get(view_id=view_id,
                                                     view_type=view_type,
                                                     toolbar=toolbar,
                                                     submenu=submenu)

        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='product_id']"):
            if check_status:
                node.set('domain', "[('bom_ids', '!=', False), '|', ('company_id', '=', False), ('company_id', '=', company_id),('check_status', '=', True)]")
            else:
                node.set('domain', "[('bom_ids', '!=', False), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")

        res['arch'] = etree.tostring(doc)

        return res
