from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate property"
    _order = "id desc"

    active = fields.Boolean(default=True)
    name = fields.Char('Property name', required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(string='Orientation', selection=[
        ('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')
        ])
    state = fields.Selection(string='State', selection=[
        ('new', 'New'), ('offer_received', 'Offer received'), ('offer_accepted', 'Offer accepted'),
        ('sold', 'Sold'), ('cancelled', 'Cancelled')
    ], required=True, default='new')
    buyer_id = fields.Many2one('res.partner', string='Buyer', index=True, copy=False)
    salesperson_id = fields.Many2one('res.users', string='Salesperson',default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")
    type_id = fields.Many2one('estate.property.type', string="Property type")
    total_area =  fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >=0)', 'The expected price must be a positive number'),
        ('check_selling_price', 'CHECK(selling_price >=0)', 'The selling price must be a positive number')
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, precision_digits=2) and not float_is_zero(record.expected_price, precision_digits=2):
                if float_compare((90 * record.expected_price / 100.0), record.selling_price, precision_digits=2) == 1:
                    raise ValidationError("The selling price must be within 90% of the expected price (from estate property)")

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = self.garden_orientation = None
            return {'warning': {
                'title': "Warning",
                'message': ('Unsetting garden area')}}

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        self.total_area = self.living_area + self.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        self.best_price = 0
        if self.offer_ids.mapped('price'):
            self.best_price = max(self.offer_ids.mapped('price'))

    def sell_action(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError('Cannot sell a cancelled property')
            else:
                record.state = 'sold'

        return True

    def cancel_action(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Cannot cancel a sold property')
            else:
                record.state = 'cancelled'
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_new_or_cancelled(self):
        for record in self:
            if record.state != 'new' and record.state != 'cancelled':
                raise UserError("Only new or cancelled properties can be deleted")