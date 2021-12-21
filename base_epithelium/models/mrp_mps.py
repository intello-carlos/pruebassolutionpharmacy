from lxml import etree
import json
from odoo import api, fields, models


class MrpProductionSchedule(models.Model):
    _inherit = 'mrp.production.schedule'

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(MrpProductionSchedule, self).fields_view_get(view_id=view_id,
                                                                 view_type=view_type,
                                                                 toolbar=toolbar,
                                                                 submenu=submenu)

        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='product_id']"):
            if check_status:
                node.set('domain', "[('check_status', '=', True)]")
            else:
                node.set('domain', "[]")

        res['arch'] = etree.tostring(doc)

        return res

    @api.model
    def get_mps_view_state(self, domain=False):
        """
        Funcion sobrecargada para cambiar el dominio de una vista hecha y llamada por javascript mediante un rpc
        @param domain: False segun la super clase
        @return: returna el llamado de la super clase
        """
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')
        if check_status:
            domain += [('product_id.check_status', '=', True)]

        return super(MrpProductionSchedule, self).get_mps_view_state(domain)
