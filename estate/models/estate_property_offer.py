from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(selection=[
    ('accepted', 'Accepted'), ('refused', 'Refused'),
    ], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_deadline")
    property_type_id = fields.Many2one(related='property_id.type_id', store=True)
    _sql_constraints = [
        ('check_price', 'CHECK(price >=0)', 'The offer price must be a positive number')
    ]

    @api.model
    def create(self, vals):
        if vals['property_id'] and vals['price']:
            existing_offers = self.search([
                ('property_id', '=', vals['property_id'])
            ])

            if existing_offers and vals['price'] < max(existing_offers.mapped('price')):
                raise UserError("No lowballing")

        offer = super().create(vals)
        offer.property_id.state = 'offer_received'

        return offer

    @api.depends("validity", "create_date")
    def _compute_deadline(self):
        for r in self:
            if r.create_date:
                r.date_deadline = r.create_date + relativedelta(days=r.validity)
            else:
                r.date_deadline = fields.Date.today() + relativedelta(days=r.validity)

    def _inverse_deadline(self):
        for r in self:
            if r.date_deadline:
                if r.create_date:
                    diff = r.date_deadline - r.create_date.date()
                    r.validity = diff.days
                else:
                    diff = r.date_deadline - fields.Date.today()
                    r.validity = diff.days

    def action_confirm(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = 'offer_accepted'

        return True

    def action_reject(self):
        for record in self:
            record.status = 'refused'

        return True

