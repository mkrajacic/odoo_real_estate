from odoo import fields, models

class EstateUser(models.Model):
    _description = "Extend User model for estate needs"
    _inherit = "res.users"

    property_ids = fields.One2many('estate.property', 'salesperson_id', string="User Properties", domain="[('date_availability','<=;',datetime.datetime.combine(context_today(), datetime.time(0, 0, 0)))]")