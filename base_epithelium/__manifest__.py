# -*- coding: utf-8 -*-
{
    'name': "Base Epithelium",

    'description': 'Modulo desarrollado para el funcionamiento basico de epithelium',
    # Long description of module's purpose

    'summary': 'Modulo base de Epithelium',
    # Short (1 phrase/line) summary of the module's purpose, used as
    # subtitle on modules listing or apps.openerp.com""",

    'author': "Intello Idea",
    'website': "http://www.intelloidea.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp_mps', 'sale', 'purchase', 'account', 'stock', 'product', 'product_expiry', 'web',
                'sale_management', 'quality', 'quality_control', 'coding_products'],
    'application': False,

    # always loaded
    'data': [
        'security/ir.model.access.csv',
    #    'report/mrp_production_templates.xml',
    #    'report/quality_label_report.xml',
    #    'report/main_reports.xml',
    #    'report/purchase_order_templates.xml',
    #    'views/res_config_settings_views.xml',
    #    'views/assets.xml',
    #    'views/production_line_views.xml',
    #    'views/sale_views.xml',
    #    'views/purchase_views.xml',
    #    'views/account_view.xml',
    #    'views/product_views.xml',
    #    'views/mrp_views.xml',
    #    'views/stock_picking.xml',
        'views/pharmaceutical_product_view.xml',
    #    'views/mrp_production.xml',
    #    'views/quality_views.xml',
    #    'views/hr_expense_views.xml',
    #    'wizard/wizard_mrp_production.xml',

    ],

    # only loaded in demonstration mode
    # 'demo': [
    # ],
}
