from odoo import models, api, fields, _

class WizardMrpProduction(models.TransientModel):
    _name = 'wizard.mrp.production'
    _description = 'wizard.mrp.production'

    users_ids = fields.Many2many('res.users',string='Users')
    message = fields.Char('Message')

    def action_create_wizard(self):
        for record in self:
            production_id = self.env['mrp.production'].browse(self._context.get('active_id'))
            model_id = self.env.ref('base_epithelium.model_mrp_production')
            type_id = self.env.ref('mail.mail_activity_data_todo')
            summary = record.message
            users = record.users_ids
            for user in users:
                activity_data = {
                    'res_id': production_id.id,
                    'res_model_id': model_id.id,
                    'activity_type_id': type_id.id,
                    'summary': summary,
                    'user_id': user.id,
                }
                self.env['mail.activity'].sudo().create(activity_data)