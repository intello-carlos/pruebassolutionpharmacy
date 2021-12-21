from odoo import api, fields, models
from odoo.tools import unquote

XML_ID = "base_epithelium._assets_primary_variables"
SCSS_URL = "/base_epithelium/static/src/scss/colors.scss"


class ResConfigSettingsMod(models.TransientModel):
    _inherit = 'res.config.settings'

    check_status = fields.Boolean('Localization',
                                  help='Company localization control')
    days_to_expiration = fields.Char('Days to Expiration', default=30)

    def set_values(self):
        res = super(ResConfigSettingsMod, self).set_values()
        parameter = self.env['ir.config_parameter'].sudo()
        parameter.set_param('res.config.settings.check_status', self.check_status)
        parameter.set_param('res.config.settings.days_to_expiration', self.days_to_expiration)
        variables = [
            'o-brand-odoo']

        colors = self.env['scss.editor.epithelium'].get_values(
            SCSS_URL, XML_ID, variables
        )

        if self.check_status:
            variables = [
                {'name': 'o-brand-odoo', 'value': "#003699"}]

        else:
            variables = [
                {'name': 'o-brand-odoo', 'value': "#7C7BAD"}]

        self.env['scss.editor.epithelium'].replace_values(
            SCSS_URL, XML_ID, variables
        )

        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsMod, self).get_values()
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')
        days_to_expiration = parameter.get_param('res.config.settings.days_to_expiration')
        res.update(
            {'check_status': check_status,
             'days_to_expiration': days_to_expiration})
        return res

    def execute(self):
        super(ResConfigSettingsMod, self).execute()

        if self.check_status:
            self._change_action_domain(True)
        else:
            self._change_action_domain(False)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _change_action_domain(self, state):
        """
        Función que busca las acciones de la vista en el los menu item y cambia los dominions de las mismas,
        se pasa por parametro un state el cual funciona como un campo activo, si state es igual a true
        se modificaran los dominions de las acciones por ('check_status",'='.True), con el fin de mostrar unicamente
        los registros con el (check_status = true) en la vista.

        @author: Juanca Perdomo - Intello Idea
        """

        # Actions for Module Sale
        sale_action = self.env.ref('sale.action_quotations_with_onboarding')
        sale_orders_action = self.env.ref('sale.action_orders')
        sale_order_to_invoice_action = self.env.ref('sale.action_orders_to_invoice')
        sale_order_upsell = self.env.ref('sale.action_orders_upselling')
        sale_product = self.env.ref('sale.product_template_action')
        sale_report_action_order = self.env.ref('sale.action_order_report_all')

        # Actions for  Module Accounting
        invoice_client_action = self.env.ref('account.action_move_out_invoice_type')
        credit_note_client_action = self.env.ref('account.action_move_out_refund_type')
        receipts_client_action = self.env.ref('account.action_move_out_receipt_type')
        account_product_action_client = self.env.ref('account.product_product_action_sellable')
        account_payment_action_client = self.env.ref('account.action_account_payments')
        account_journal_action = self.env.ref('account.open_account_journal_dashboard_kanban')

        bills_provider_action = self.env.ref('account.action_move_in_invoice_type')
        refund_provider_action = self.env.ref('account.action_move_in_refund_type')
        receipts_provider_action = self.env.ref('account.action_move_in_receipt_type')
        account_payment_action_provider = self.env.ref('account.action_account_payments_payable')
        account_product_action_provider = self.env.ref('account.product_product_action_purchasable')

        journal_action = self.env.ref('account.action_account_journal_form')

        # Actions for Module Purchase
        request_quotation_action = self.env.ref('purchase.purchase_rfq')
        purchase_order_action = self.env.ref('purchase.purchase_form_action')
        purchase_product = self.env.ref('purchase.product_normal_action_puchased')
        purchase_report = self.env.ref('purchase.action_purchase_order_report_all')

        # Actions for Module Inventory
        transference_action = self.env.ref('stock.action_picking_tree_all')
        inventory_adjust_action = self.env.ref('stock.action_inventory_form')
        scrap_orders_action = self.env.ref('stock.action_stock_scrap')
        product_stock = self.env.ref('stock.product_template_action_product')
#Carlos        reordering_rules_action = self.env.ref('stock.action_orderpoint_form')
        product_move_line_action = self.env.ref('stock.stock_move_line_action')
        stock_move_action = self.env.ref('stock.stock_move_action')
        operation_types_action = self.env.ref('stock.action_picking_type_list')
        product_category = self.env.ref('product.product_category_action_form')
        product_code = self.env.ref('coding_products.action_coding_products')

        # Action for Module Manufacturing
        manufacturing_order_action = self.env.ref('mrp.mrp_production_action')
        unbuild_order_action = self.env.ref('mrp.mrp_unbuild')
        manufacturing_product_action = self.env.ref('mrp.product_template_action')
        production_lines_action = self.env.ref('base_epithelium.production_lines_action')
        master_production_action = self.env.ref('mrp_mps.action_mrp_mps')
        bills_materials_action = self.env.ref('mrp.mrp_bom_form_action')
        production_order = self.env.ref('mrp.mrp_production_report')
        work_order_report = self.env.ref('mrp.mrp_workorder_report')
        work_order_todo = self.env.ref('mrp.mrp_workorder_todo')

        # Action for Module Quality
        quality_point = self.env.ref('quality_control.quality_point_action')
        quality_check = self.env.ref('quality_control.quality_check_action_main')
        quality_alert = self.env.ref('quality_control.quality_alert_action_check')
        quality_team = self.env.ref('quality_control.quality_alert_action_team')
        quality_team_check = self.env.ref('quality_control.quality_check_action_team')

        quality_check_report = self.env.ref('quality_control.quality_check_action_report')
        quality_alert_report = self.env.ref('quality_control.quality_alert_action_report')

        # Stock Actions
        stock_picking_type_action = self.env.ref('stock.stock_picking_type_action')
        stock_quant_dashboard = self.env.ref('stock.dashboard_open_quants')
        stock_quantity_report = self.env.ref('stock.report_stock_quantity_action')
#Carlos        stock_inventory_valuation = self.env.ref('stock_account.action_stock_inventory_valuation')

        # account accountant

        active_id = unquote("active_id")

        if state:
            # Action Module Sale
            sale_action.update({'domain': [('check_status', '=', True)]})
            sale_orders_action.update(
                {'domain': [('check_status', '=', True), ('state', 'not in', ('draft', 'sent', 'cancel'))]})
            sale_order_to_invoice_action.update(
                {'domain': [('invoice_status', '=', 'to invoice'), ('check_status', '=', True)]})
            sale_order_upsell.update({'domain': [('check_status', '=', True), ('invoice_status', '=', 'upselling')]})
            sale_product.update({'domain': [('check_status', '=', True)]})
            sale_report_action_order.update({'domain': [('order_id.check_status', '=', True)]})

            # Action Module Accounting
#Carlos            invoice_client_action.update({'domain': [('check_status', '=', True), ('type', '=', 'out_invoice')]})
            invoice_client_action.update({'domain': [('check_status', '=', True), ('move_type', '=', 'out_invoice')]})       
#Carlos            credit_note_client_action.update({'domain': [('check_status', '=', True), ('type', '=', 'out_refund')]})
            credit_note_client_action.update({'domain': [('check_status', '=', True), ('move_type', '=', 'out_refund')]})
#Carlos            receipts_client_action.update({'domain': [('check_status', '=', True), ('type', '=', 'out_receipt')]})
            receipts_client_action.update({'domain': [('check_status', '=', True), ('move_type', '=', 'out_receipt')]})
            account_product_action_client.update({'domain': [('check_status', '=', True)]})
            account_payment_action_client.update({'domain': [('journal_id.check_status', '=', True)]})
            account_journal_action.update({'domain': [('check_status', '=', True)]})

#Carlos            bills_provider_action.update({'domain': [('check_status', '=', True), ('type', '=', 'in_invoice')]})
            bills_provider_action.update({'domain': [('check_status', '=', True), ('move_type', '=', 'in_invoice')]})
#Carlos            refund_provider_action.update({'domain': [('type', '=', 'in_refund'), ('check_status', '=', True)]})
            refund_provider_action.update({'domain': [('move_type', '=', 'in_refund'), ('check_status', '=', True)]})
#Carlos            receipts_provider_action.update({'domain': [('check_status', '=', True), ('type', '=', 'in_receipt')]})
            receipts_provider_action.update({'domain': [('check_status', '=', True), ('move_type', '=', 'in_receipt')]})
            account_payment_action_provider.update({'domain': [('journal_id.check_status', '=', True)]})
            account_product_action_provider.update({'domain': [('check_status', '=', True)]})
            journal_action.update({'domain': [('check_status', '=', True)]})

            # Action Module Purchase
            request_quotation_action.update({'domain': [('check_status', '=', True)]})
            purchase_order_action.update(
                {'domain': [('state', 'in', ('purchase', 'done')), ('check_status', '=', True)]})
            purchase_product.update({'domain': [('check_status', '=', True)]})
            purchase_report.update({'domain': [('order_id.check_status', '=', True)]})

            # Action Module Inventory
            transference_action.update({'domain': [('check_status', '=', True)]})
            inventory_adjust_action.update({'domain': [('product_ids.check_status', '=', True)]})
            scrap_orders_action.update({'domain': [('product_id.check_status', '=', True)]})
            product_stock.update({'domain': [('check_status', '=', True)]})
#Carlos            reordering_rules_action.update({'domain': [('product_id.check_status', '=', True)]})
            product_move_line_action.update({'domain': [('product_id.check_status', '=', True)]})
            stock_move_action.update({'domain': [('product_id.check_status', '=', True)]})
            operation_types_action.update({'domain': [('check_status', '=', True)]})
            product_category.update({'domain': [('check_status', '=', True)]})
            product_code.update({'domain': [('check_status', '=', True)]})

            # Action Module Manufacturing
            manufacturing_order_action.update(
                {'domain': [('picking_type_id.active', '=', True), ('check_status', '=', True)]})
            unbuild_order_action.update({'domain': [('product_id.check_status', '=', True)]})
            manufacturing_product_action.update({'domain': [('check_status', '=', True)]})
            production_lines_action.update({'domain': [('check_status', '=', True)]})
            bills_materials_action.update({'domain': [('check_status', '=', True)]})
            production_order.update({'domain': [('check_status', '=', True)]})
            work_order_report.update({'domain': [('product_id.check_status', '=', True)]})
            work_order_todo.update({'domain': [('product_id.check_status', '=', True)]})

            # Action Module Quality
            quality_point.update({'domain': [('check_status', '=', True)]})
            quality_check.update({'domain': [('check_status', '=', True)]})
            quality_alert.update({'domain': [('check_status', '=', True)]})
            quality_check_report.update({'domain': [('check_status', '=', True)]})
            quality_alert_report.update({'domain': [('check_status', '=', True)]})
            quality_team.update({'domain': [('team_id', '=', active_id), ('check_status', '=', True)]})
            quality_team_check.update({'domain': [('team_id', '=', active_id), ('check_status', '=', True)]})

            # Stock
            stock_picking_type_action.update({'domain': [('check_status', '=', True)]})
#            stock_inventory_valuation.update({'domain': [('product_id.type', '=', 'product'), '|',
#                                                         ('product_id.check_status', '=', True),
#                                                         ('product_tmpl_id.check_status', '=', True)]})
            stock_quantity_report.update({'domain': [('warehouse_id', '!=', False), '|',
                                                     ('product_id.check_status', '=', True),
                                                     ('product_tmpl_id.check_status', '=', True)]})
            stock_quant_dashboard.update(
                {'domain': ['|', ('product_id.check_status', '=', True), ('product_tmpl_id.check_status', '=', True)]})


        else:
            # Action Module Sale
            sale_action.update({'domain': []})
            sale_orders_action.update({'domain': [('state', 'not in', ('draft', 'sent', 'cancel'))]})
            sale_order_to_invoice_action.update({'domain': [('invoice_status', '=', 'to invoice')]})
            sale_order_upsell.update({'domain': [('invoice_status', '=', 'upselling')]})
            sale_product.update({'domain': []})
            sale_report_action_order.update({'domain': []})

            # Action Module Accounting
#Carlos            invoice_client_action.update({'domain': [('type', '=', 'out_invoice')]})
#Carlos            credit_note_client_action.update({'domain': [('type', '=', 'out_refund')]})
#Carlos            receipts_client_action.update({'domain': [('type', '=', 'out_receipt')]})
            invoice_client_action.update({'domain': [('move_type', '=', 'out_invoice')]})
            credit_note_client_action.update({'domain': [('move_type', '=', 'out_refund')]})
            receipts_client_action.update({'domain': [('move_type', '=', 'out_receipt')]})
            account_product_action_client.update({'domain': []})
            account_payment_action_client.update({'domain': []})
            account_journal_action.update({'domain': []})

#Carlos            bills_provider_action.update({'domain': [('type', '=', 'in_invoice')]})
#Carlos            refund_provider_action.update({'domain': [('type', '=', 'in_refund')]})
#Carlos            receipts_provider_action.update({'domain': [('type', '=', 'in_receipt')]})
            bills_provider_action.update({'domain': [('move_type', '=', 'in_invoice')]})
            refund_provider_action.update({'domain': [('move_type', '=', 'in_refund')]})
            receipts_provider_action.update({'domain': [('move_type', '=', 'in_receipt')]})
            account_payment_action_provider.update({'domain': []})
            account_product_action_provider.update({'domain': []})
            journal_action.update({'domain': []})

            # Action Module Purchase
            request_quotation_action.update({'domain': []})
            purchase_order_action.update({'domain': [('state', 'in', ('purchase', 'done'))]})
            purchase_product.update({'domain': []})
            purchase_report.update({'domain': []})

            # Action Module Inventory
            transference_action.update({'domain': []})
            inventory_adjust_action.update({'domain': []})
            scrap_orders_action.update({'domain': []})
            product_stock.update({'domain': []})
#            reordering_rules_action.update({'domain': []})
            product_move_line_action.update({'domain': []})
            stock_move_action.update({'domain': []})
            operation_types_action.update({'domain': []})
            product_category.update({'domain': []})
            product_code.update({'domain': []})

            # Action Module Manufacturing
            manufacturing_order_action.update({'domain': [('picking_type_id.active', '=', True)]})
            unbuild_order_action.update({'domain': []})
            manufacturing_product_action.update({'domain': []})
            production_lines_action.update({'domain': []})
            bills_materials_action.update({'domain': []})
            production_order.update({'domain': []})
            work_order_report.update({'domain': []})
            work_order_todo.update({'domain': []})

            # Action Quality
            quality_point.update({'domain': []})
            quality_check.update({'domain': []})
            quality_alert.update({'domain': []})
            quality_check_report.update({'domain': []})
            quality_alert_report.update({'domain': []})
            quality_team.update({'domain': [('team_id', '=', active_id)]})
            quality_team_check.update({'domain': [('team_id', '=', active_id)]})

            # Stock
            stock_picking_type_action.update({'domain': []})
            stock_quant_dashboard.update({'domain': []})
            stock_quantity_report.update({'domain': [('warehouse_id', '!=', False)]})
#            stock_inventory_valuation.update({'domain': [('product_id.type', '=', 'product')]})
