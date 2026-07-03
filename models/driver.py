from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TransportDriver(models.Model):
    _name = 'transport.driver'
    _description = 'Transport Driver'
    _rec_name = 'name'
    _order = 'driver_code asc'

    _sql_constraints = [
        (
            'unique_driver_code',
            'unique(driver_code)',
            'Driver Code already exists!'
        ),
        (
            'unique_nic',
            'unique(nic)',
            'NIC Number already exists!'
        ),
        (
            'unique_license',
            'unique(license_number)',
            'License Number already exists!'
        ),
    ]

    driver_code = fields.Char(
        string="Driver Code",
        default="New",
        readonly=True,
        copy=False
    )

    photo = fields.Image(string="Photo")
    name = fields.Char(string="Driver Name", required=True)
    nic = fields.Char(string="NIC Number")
    phone = fields.Char(string="Phone Number", required=True)
    email = fields.Char(string="Email")
    address = fields.Text(string="Address")
    emergency_contact = fields.Char(string="Emergency Contact")

    license_number = fields.Char(string="License Number", required=True)
    license_class = fields.Selection([
        ('A', 'A - Motorcycle'),
        ('B', 'B - Car/Van'),
        ('C', 'C - Heavy Vehicle'),
        ('D', 'D - Bus')
    ], string="License Class", required=True)

    license_expiry = fields.Date(string="License Expiry")

    license_expiry_warning = fields.Boolean(
        string="License Expiry Warning",
        compute="_compute_license_expiry_warning"
    )

    license_expiry_message = fields.Char(
        string="License Expiry Message",
        compute="_compute_license_expiry_warning"
    )

    experience_years = fields.Integer(string="Experience Years")

    status = fields.Selection([
        ('active', 'Active'),
        ('leave', 'On Leave'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive')
    ], string="Status", default='active', required=True)

    @api.model
    def create(self, vals):
        if vals.get('driver_code', 'New') == 'New':
            vals['driver_code'] = self.env['ir.sequence'].next_by_code(
                'transport.driver'
            ) or 'New'
        return super().create(vals)

    @api.depends('license_expiry')
    def _compute_license_expiry_warning(self):
        today = fields.Date.today()

        for record in self:
            record.license_expiry_warning = False
            record.license_expiry_message = ""

            if record.license_expiry:
                days_left = (record.license_expiry - today).days

                if days_left < 0:
                    record.license_expiry_warning = True
                    record.license_expiry_message = "License has expired!"

                elif days_left <= 30:
                    record.license_expiry_warning = True
                    record.license_expiry_message = (
                        f"License will expire in {days_left} days."
                    )

    @api.constrains('experience_years')
    def _check_experience_years(self):
        for record in self:
            if record.experience_years < 0:
                raise ValidationError("Experience years cannot be negative.")

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.driver_code} - {record.name}"
            result.append((record.id, name))
        return result