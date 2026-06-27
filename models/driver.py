from odoo import models, fields


class TransportDriver(models.Model):
    _name = 'transport.driver'
    _description = 'Transport Driver'

    name = fields.Char(string="Driver Name", required=True)
    phone = fields.Char(string="Phone Number")
    license_number = fields.Char(string="License Number")
    license_expiry = fields.Date(string="License Expiry")

    status = fields.Selection([
        ('active', 'Active'),
        ('leave', 'On Leave'),
        ('inactive', 'Inactive')
    ], string="Status", default='active')