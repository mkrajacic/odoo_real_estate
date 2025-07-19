from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate property tag"
    _order = "name"

    name = fields.Char('Tag name', required=True)
    color = fields.Integer('Color')
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The tag name must be unique')
    ]