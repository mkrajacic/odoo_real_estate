from odoo import fields, models, api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type"
    _order = "sequence, name"

    name = fields.Char('Type name', required=True)
    property_ids = fields.One2many('estate.property', 'type_id', string="Properties")
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string="Offers")
    offer_count = fields.Integer(compute='_compute_offer_count')
    sequence = fields.Integer('Sequence', default=1, help="idk what im doing")
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The tag name must be unique')
    ]

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)