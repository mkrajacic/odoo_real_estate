from odoo import fields, models, Command

class EstateAccountProperty(models.Model):
    _description = "Extend estate property for estate account needs"
    _inherit = "estate.property"

    def sell_action(self):
        for prop in self:
            values = {}
            values['partner_id'] = prop.buyer_id.id
            values['move_type'] = 'out_invoice'
            values['invoice_line_ids'] = [
                Command.create({
                    "name": "Monica",
                    "quantity": 1,
                    "price_unit": (6 * prop.selling_price) / 100.0
                }),
                Command.create({
                    "name": "Silent witch",
                    "quantity": 1,
                    "price_unit": 100.0
                })
            ]
            account_move = self.env['account.move'].create(values)
        return super().sell_action()